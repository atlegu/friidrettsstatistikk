# uavhengig.R — A3 «Debutalder»: uavhengig reimplementasjon i R (audit fase 3).
# Skrevet fra metodeteksten (manus §2); region utelatt med vilje (vakuøs — DATA_AUDIT A3-1):
# reproduksjon av de publiserte tallene UTEN region er beviset for at fjerningen er tallnøytral.
# Output: audit/r_out/*.csv

suppressMessages({library(data.table); library(survival)})
setwd(dirname(dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])))))
dir.create("audit/r_out", showWarnings = FALSE)
z975 <- qnorm(.975)

utv <- fread("data_private/utovere.csv"); setnames(utv, "id", "athlete_id")
r <- fread("data_private/resultater.csv")
r <- merge(r, utv, by = "athlete_id")
r <- r[status == "OK"]
r[, date := as.IDate(date)][, aar := year(date)][, alder := aar - birth_year]

# A3-2: utøvere med første resultat før fylte 10 (debut forskjøvet til 10+)
forste_alder <- r[, .(min_alder = min(alder)), by = athlete_id]
fwrite(data.table(utovere_forste_res_under_10 = nrow(forste_alder[min_alder < 10])),
       "audit/r_out/debut_under10.csv")

r <- r[alder >= 10]

# ---- Debut, utfall, volum ------------------------------------------------------------------
setorder(r, date)
base <- r[, .SD[1], by = athlete_id][, .(athlete_id, debut_dato = date)]
base <- merge(base, utv, by = "athlete_id")
base[, debut_aar := year(debut_dato)][, debut_alder := debut_aar - birth_year]
base <- base[gender %chin% c("M", "F")]
base[, kvartal := (month(as.IDate(birth_date)) - 1) %/% 3 + 1]

arsvol <- r[, .(dager = uniqueN(date)), by = .(athlete_id, alder)]
aktiv17_sett <- unique(arsvol[alder == 17, athlete_id])
v1617 <- arsvol[alder %in% 16:17, .(vol_16_17 = sum(dager)), by = athlete_id]
base <- merge(base, v1617, by = "athlete_id", all.x = TRUE)
vdeb <- merge(base[, .(athlete_id, debut_alder)], arsvol,
              by.x = c("athlete_id", "debut_alder"), by.y = c("athlete_id", "alder"), all.x = TRUE)
base[, vol_debutaar := vdeb$dager[match(athlete_id, vdeb$athlete_id)]]

sen <- r[alder >= 20, .N, by = .(athlete_id, aar)]
base[, senior := as.integer(athlete_id %in% sen[N >= 2, unique(athlete_id)])]
base[, senior_min1 := as.integer(athlete_id %in% r[alder >= 20, unique(athlete_id)])]
base[, siste_alder := r[, max(alder), by = athlete_id][match(base$athlete_id, athlete_id), V1]]
base[, aktiv_naa := athlete_id %in% r[aar >= 2025, unique(athlete_id)]]
base[, aktiv_i_17 := athlete_id %in% aktiv17_sett]

# ---- Klubb i debutsesongen (modal, tie-break minste som streng) ---------------------------
dsr <- merge(r[, .(athlete_id, aar, club_id)], base[, .(athlete_id, debut_aar)], by = "athlete_id")
dsr <- dsr[aar == debut_aar & !is.na(club_id) & club_id != ""]
modal_klubb <- dsr[, .N, by = .(athlete_id, club_id)][
  order(athlete_id, -N, as.character(club_id)), .SD[1], by = athlete_id]
base <- merge(base, modal_klubb[, .(athlete_id, club_id)], by = "athlete_id", all.x = TRUE)
base[, klubbstorrelse := .N, by = club_id]
base[is.na(club_id), klubbstorrelse := NA_integer_]
base[, log_klubb := log1p(klubbstorrelse)]
base[is.na(log_klubb), log_klubb := median(base$log_klubb, na.rm = TRUE)]

base[, covid_debut := debut_aar %in% 2020:2021]
base[, kohort_primar := birth_year %between% c(2001, 2005)]
prim <- base[kohort_primar & debut_alder %between% c(10, 16)]
prim[, debut_kat := factor(pmin(debut_alder, 17), levels = 10:17)]
prim[, bk := factor(birth_year)]

# ---- Utvalgskontroll mot analysedata -------------------------------------------------------
ad <- fread("data_private/analysedata.csv")
adp <- ad[kohort_primar == TRUE & debut_10_16 == TRUE]
m <- merge(prim[, .(athlete_id, debut_alder, senior)],
           adp[, .(athlete_id, p_debut = debut_alder, p_senior = senior)],
           by = "athlete_id", all = TRUE)
fwrite(data.table(n_prim_R = nrow(prim), n_prim_py = nrow(adp),
                  kun_R = sum(is.na(m$p_debut)), kun_py = sum(is.na(m$debut_alder)),
                  ulik_debutalder = sum(m$debut_alder != m$p_debut, na.rm = TRUE),
                  ulik_senior = sum(m$senior != m$p_senior, na.rm = TRUE),
                  seniorer_R = sum(prim$senior)), "audit/r_out/utvalg.csv")

# ---- Logit-hjelpere ------------------------------------------------------------------------
or_rader <- function(m, merk, n, hendelser) {
  s <- summary(m)$coefficients
  data.table(analyse = merk, variabel = rownames(s), OR = exp(s[, 1]),
             KI_lav = exp(s[, 1] - z975 * s[, 2]), KI_hoy = exp(s[, 1] + z975 * s[, 2]),
             p = s[, 4], n = n, hendelser = hendelser)
}

ut <- list()
# H1 kategorisk og lineær (uten region — vakuitetsbevis)
m_kat <- glm(senior ~ debut_kat + gender + bk + log_klubb, binomial, prim)
m_lin <- glm(senior ~ debut_alder + gender + bk + log_klubb, binomial, prim)
ut$h1k <- or_rader(m_kat, "H1_kategorisk", nrow(prim), sum(prim$senior))
ut$h1l <- or_rader(m_lin, "H1_trend", nrow(prim), sum(prim$senior))
lr <- 2 * (logLik(m_kat) - logLik(m_lin))
ut$lrt <- data.table(analyse = "LRT", variabel = "kat_vs_lin", OR = as.numeric(lr),
                     KI_lav = attr(logLik(m_kat), "df") - attr(logLik(m_lin), "df"),
                     KI_hoy = 1 - pchisq(as.numeric(lr), attr(logLik(m_kat), "df") - attr(logLik(m_lin), "df")),
                     p = NA, n = nrow(prim), hendelser = sum(prim$senior))

# H3-landmark (r1-definisjonen: aktiv i 17-årssesongen)
lm_ <- prim[aktiv_i_17 == TRUE]
lm_[, v := fifelse(is.na(vol_16_17), 0, as.numeric(vol_16_17))]
lm_[, vol_z := (v - mean(v)) / sd(v)]
ut$h3u <- or_rader(glm(senior ~ debut_alder + gender + bk, binomial, lm_),
                   "r1_H3_uten_volum", nrow(lm_), sum(lm_$senior))
ut$h3m <- or_rader(glm(senior ~ debut_alder + vol_z + gender + bk, binomial, lm_),
                   "r1_H3_med_volum", nrow(lm_), sum(lm_$senior))
ut$h3info <- data.table(analyse = "landmark_info", variabel = c("n_ny", "seniorer_ny", "idle17_tilbake"),
                        OR = c(nrow(lm_), sum(lm_$senior), sum(prim[aktiv_i_17 == FALSE, senior])),
                        KI_lav = NA, KI_hoy = NA, p = NA, n = NA, hendelser = NA)

# Debut 17-19 (uten utfallsoverlapp: debut >=20 utelatt)
d1719 <- base[kohort_primar & debut_alder %between% c(10, 19)]
d1719[, debut_kat := factor(pmin(debut_alder, 17), levels = 10:17)]
d1719[, bk := factor(birth_year)]
ut$d17 <- or_rader(glm(senior ~ debut_kat + gender + bk + log_klubb, binomial, d1719),
                   "r1_debut_17_19", nrow(d1719), sum(d1719$senior))

# Kjønnsinteraksjon
pi_ <- copy(prim)[, kvinne := as.numeric(gender == "F")][, dxk := debut_alder * kvinne]
ut$kji <- or_rader(glm(senior ~ debut_alder + kvinne + dxk + bk + log_klubb, binomial, pi_),
                   "r1_kjonnsinteraksjon", nrow(pi_), sum(pi_$senior))

# Robusthet (hovedradene)
ut$r1 <- or_rader(glm(senior ~ debut_alder + gender + bk + log_klubb, binomial,
                      prim[covid_debut == FALSE]), "uten_covid_debut",
                  nrow(prim[covid_debut == FALSE]), sum(prim[covid_debut == FALSE, senior]))
ut$r2 <- or_rader(glm(senior_min1 ~ debut_alder + gender + bk + log_klubb, binomial, prim),
                  "utfall_min1", nrow(prim), sum(prim$senior_min1))
pv <- copy(prim)[, vz := { v <- fifelse(is.na(vol_debutaar), 0, as.numeric(vol_debutaar)); (v - mean(v)) / sd(v) }]
ut$r3 <- or_rader(glm(senior ~ debut_alder + vz + gender + bk + log_klubb, binomial, pv),
                  "betinget_debutvolum", nrow(pv), sum(pv$senior))
for (kn in list(c("kohort_2001_2003", 2001, 2003), c("kohort_2004_2005", 2004, 2005))) {
  g <- prim[birth_year %between% c(as.integer(kn[2]), as.integer(kn[3]))]
  g[, bk := droplevels(bk)]
  ut[[kn[1]]] <- or_rader(glm(senior ~ debut_alder + gender + bk + log_klubb, binomial, g),
                          kn[1], nrow(g), sum(g$senior))
}

fwrite(rbindlist(ut), "audit/r_out/logit.csv")

# ---- Cox med alder som tidsskala og forsinket inntreden -----------------------------------
cx <- copy(prim)
cx[, slutt := pmax(siste_alder, debut_alder) + 0.5]
cx[, hendelse := as.integer(!aktiv_naa)]
cx[, kvinne := as.numeric(gender == "F")]
cx[, kohort_c := birth_year - mean(birth_year)]
cm <- coxph(Surv(debut_alder, slutt, hendelse) ~ debut_alder + kvinne + kohort_c + log_klubb,
            data = cx)
s <- summary(cm)$coefficients
fwrite(data.table(variabel = rownames(s), HR = exp(s[, 1]),
                  KI_lav = exp(s[, 1] - z975 * s[, 3]), KI_hoy = exp(s[, 1] + z975 * s[, 3])),
       "audit/r_out/cox.csv")

# ---- Retention k år etter debut (Wilson) ---------------------------------------------------
aktiv_nokkel <- paste(arsvol$athlete_id, arsvol$alder)
rk <- rbindlist(lapply(10:16, function(da) rbindlist(lapply(0:5, function(k) {
  g <- prim[debut_alder == da & birth_year + da + k <= 2025]
  if (!nrow(g)) return(NULL)
  tr <- sum(paste(g$athlete_id, da + k) %chin% aktiv_nokkel)
  n <- nrow(g); ph <- tr / n; zz <- z975
  sent <- (ph + zz^2 / (2 * n)) / (1 + zz^2 / n)
  halvt <- zz * sqrt(ph * (1 - ph) / n + zz^2 / (4 * n^2)) / (1 + zz^2 / n)
  data.table(debut_alder = da, k = k, n = n, aktive = tr, andel = ph,
             ki_lav = sent - halvt, ki_hoy = sent + halvt)
}))))
fwrite(rk, "audit/r_out/retention.csv")

cat("uavhengig A3 ferdig\n")
