# uavhengig.R — A1 «Stagnasjon før exit»: uavhengig reimplementasjon i R (audit fase 3).
# Bygget fra metodeteksten (manus §2) og ANALYSEPLAN; Tyrving-poengene leses fra den
# validerte delte komponenten (audit/tyrving_scored.csv, jf. eksport_tyrving.py).
# Region er utelatt med vilje: kolonnen er NA for alle (DATA_AUDIT A1-1), og eksakt
# reproduksjon uten den beviser at fjerningen er tallnøytral.
# CV-baserte størrelser (AUC/DeLong/kalibrering) verifiseres separat (delong_bro).
# Output: audit/r_out/*.csv

suppressMessages({library(data.table); library(survival)})
setwd(dirname(dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])))))
dir.create("audit/r_out", showWarnings = FALSE)
z975 <- qnorm(.975)

# Importkopier (audit 30.10.2026): brettraden i lengde/tresteg fjernes når en OK-rad under
# sonekoden har samme utøver, resultat og vind på samme dato (sonetvilling) eller 1-6 dager
# senere (flerdagsstevner: kopien fikk stevnets startdato); deretter eksakte dubletter (utøver,
# dato, øvelse, resultat, vind, runde) blant OK-radene, lavest id beholdes (C-sortering).
fjern_kopier <- function(r) {
  r <- copy(r)
  r[, `:=`(vk = fifelse(is.na(wind), -99, round(wind, 1)),
           rk = fifelse(is.na(round) | round == "", "NA", as.character(round)), rad = .I)]
  sone <- unique(r[status == "OK" & event_code %chin% c("lengde_sone_05m", "tresteg_sone_05m"),
                   .(athlete_id, date, performance_value, vk,
                     brett = fifelse(event_code == "lengde_sone_05m", "lengde", "tresteg"))])
  brett <- r[status == "OK" & event_code %chin% c("lengde", "tresteg")]
  tv <- brett[sone, on = .(athlete_id, date, performance_value, vk, event_code = brett), nomatch = 0L, rad]
  fd <- brett[!(rad %in% tv) & !is.na(performance_value)][
    sone[!is.na(performance_value)], on = .(athlete_id, performance_value, vk, event_code = brett),
    nomatch = 0L, allow.cartesian = TRUE, .(rad, dager = as.integer(as.IDate(i.date) - as.IDate(x.date)))][
    dager >= 1 & dager <= 6, unique(rad)]
  kand <- r[status == "OK" & !(rad %in% c(tv, fd))]
  setorderv(kand, "id")
  du <- kand[duplicated(kand, by = c("athlete_id", "date", "event_code", "performance_value", "vk", "rk")), rad]
  cat(sprintf("fjern_kopier: %d sonetvillinger, %d flerdagskopier, %d eksakte dubletter\n",
              length(unique(tv)), length(fd), length(du)))
  r[!(rad %in% c(tv, fd, du))][, c("vk", "rk", "rad") := NULL][]
}

utv <- fread("data_private/utovere.csv"); setnames(utv, "id", "athlete_id")
r <- fjern_kopier(fread("data_private/resultater.csv", drop = "birth_year"))
r <- merge(r, utv, by = "athlete_id")
r <- r[status == "OK"]
r[, date := as.IDate(date)][, aar := year(date)][, alder := aar - birth_year]

# ---- Landmark og base ----------------------------------------------------------------------
har1314 <- unique(r[alder %in% 13:14, athlete_id])
har1516 <- unique(r[alder %in% 15:16, athlete_id])
landmark <- intersect(har1314, har1516)
base <- utv[athlete_id %in% landmark]
base <- base[gender %chin% c("M", "F")]
base[, kvartal := (month(as.IDate(birth_date)) - 1) %/% 3 + 1]

rl <- r[athlete_id %in% base$athlete_id]
w1 <- rl[alder %in% 13:14]

modal1 <- function(dt, kol) {
  dt[!is.na(get(kol)) & get(kol) != "", .N, by = c("athlete_id", kol)][
    order(athlete_id, -N, as.character(get(kol))), .SD[1], by = athlete_id][, c("athlete_id", kol), with = FALSE]
}
hg <- modal1(w1, "event_category"); setnames(hg, "event_category", "hovedgruppe")
base <- merge(base, hg, by = "athlete_id", all.x = TRUE)

# ---- Tyrving (delt komponent) + vindgyldighet ----------------------------------------------
sc <- fread("audit/tyrving_scored.csv")
sc <- sc[athlete_id %chin% base$athlete_id & id %chin% r$id]
ev <- fread("data_private/events.csv")
vindov <- ev[tolower(as.character(wind_measured)) == "true", code]
# vindlovlig = ikke vindøvelse, innendørs, eller registrert lovlig vind (manglende måling ute: nei)
inne_id <- merge(r[, .(id, meet_id)], fread("data_private/meets.csv")[, .(meet_id = id, indoor)],
                 by = "meet_id")[tolower(as.character(indoor)) == "true", id]
sc <- merge(sc, r[, .(id, vind_r = wind)], by = "id", all.x = TRUE)
sc[, vindgyldig := !(event_code %chin% vindov) | id %chin% inne_id |
     tolower(as.character(is_wind_legal)) %in% "true" |
     (is.na(is_wind_legal) & !is.na(vind_r) & vind_r <= 2)]
sc <- merge(sc, base[, .(athlete_id, hovedgruppe)], by = "athlete_id")

mean3 <- function(x) if (!length(x)) NA_real_ else mean(sort(x, decreasing = TRUE)[seq_len(min(3, length(x)))])

poeng <- function(aldre, grp_kol = "hovedgruppe", kun_vind = FALSE, grp_tab = NULL) {
  dd <- sc[alder %in% aldre]
  if (kun_vind) dd <- dd[vindgyldig == TRUE]
  if (!is.null(grp_tab)) {
    dd <- merge(dd[, -"hovedgruppe"], grp_tab, by = "athlete_id")
    dd <- dd[event_category == bg]
  } else dd <- dd[event_category == hovedgruppe]
  dd[, .(m3 = mean3(tyrving), mx = max(tyrving), ma = mean(tyrving), k = .N), by = athlete_id]
}

p_w1 <- poeng(13:14); p_w2 <- poeng(15:16)
p13 <- poeng(13); p14 <- poeng(14)
p_w1v <- poeng(13:14, kun_vind = TRUE); p_w2v <- poeng(15:16, kun_vind = TRUE)
w2sc <- sc[alder %in% 15:16][event_category != "", .(m3 = mean3(tyrving)), by = .(athlete_id, event_category)]
bgt <- w2sc[order(athlete_id, -m3, as.character(event_category)), .SD[1], by = athlete_id][
  , .(athlete_id, bg = event_category)]
p_w1bg <- poeng(13:14, grp_tab = bgt); p_w2bg <- poeng(15:16, grp_tab = bgt)

hent <- function(tab, kol) tab[match(base$athlete_id, athlete_id), get(kol)]
base[, k13 := fifelse(is.na(hent(p_w1, "k")), 0L, as.integer(hent(p_w1, "k")))]
base[, k15 := fifelse(is.na(hent(p_w2, "k")), 0L, as.integer(hent(p_w2, "k")))]
base[, niva_w1 := hent(p_w1, "m3")][, niva_w2 := hent(p_w2, "m3")]
base[, delta := niva_w2 - niva_w1]
base[, delta_max := hent(p_w2, "mx") - hent(p_w1, "mx")]
base[, delta_all := hent(p_w2, "ma") - hent(p_w1, "ma")]
base[, delta_vind := hent(p_w2v, "m3") - hent(p_w1v, "m3")]
base[, delta_bg2 := hent(p_w2bg, "m3") - hent(p_w1bg, "m3")]
# nivå og antall i beste gruppe (gruppekonsistent switcher-variant, Atles beslutning 30.10.2026)
base[, bestgruppe := bgt$bg[match(athlete_id, bgt$athlete_id)]]
base[, niva_w1_bg := hent(p_w1bg, "m3")]
base[, k13_bg := fifelse(is.na(hent(p_w1bg, "k")), 0L, as.integer(hent(p_w1bg, "k")))]
base[, k15_bg := fifelse(is.na(hent(p_w2bg, "k")), 0L, as.integer(hent(p_w2bg, "k")))]
base[, delta_nk := hent(p14, "m3") - hent(p13, "m3")]

# ---- Volum, utfall, klubb ------------------------------------------------------------------
for (nv in list(c("vol1314", 13, 14), c("vol1516", 15, 16))) {
  v <- rl[alder %in% as.integer(nv[2]):as.integer(nv[3]), .(d = uniqueN(date)), by = athlete_id]
  base[, (nv[1]) := fifelse(is.na(v$d[match(athlete_id, v$athlete_id)]), 0L,
                            v$d[match(athlete_id, v$athlete_id)])]
}
sen <- rl[alder >= 20, .N, by = .(athlete_id, aar)]
base[, senior := as.integer(athlete_id %in% sen[N >= 2, unique(athlete_id)])]
base[, senior_min1 := as.integer(athlete_id %in% rl[alder >= 20, unique(athlete_id)])]
base[, aktiv18 := as.integer(athlete_id %in% rl[alder >= 18, unique(athlete_id)])]
s2021 <- rl[alder %in% 20:21, .N, by = .(athlete_id, aar)]
base[, senior_20_21 := as.integer(athlete_id %in% s2021[N >= 2, unique(athlete_id)])]
base[, siste_alder := rl[, max(alder), by = athlete_id][match(base$athlete_id, athlete_id), V1]]

kl <- modal1(w1, "club_id"); setnames(kl, "club_id", "club_id")
base <- merge(base, kl, by = "athlete_id", all.x = TRUE)
base[, klubbstorrelse := .N, by = club_id]
base[is.na(club_id), klubbstorrelse := NA_integer_]
base[, log_klubb := log1p(klubbstorrelse)]

base[, kohort := fifelse(birth_year <= 2001, "A", "B")]
base[, kohort_primar := birth_year %between% c(1998, 2005)]
base[, skaarbar := k13 >= 1 & k15 >= 1]

prim0 <- base[kohort_primar & skaarbar]
celler <- prim0[!is.na(hovedgruppe), .N, by = .(gender, hovedgruppe)]
smaa <- celler[N < 20]
base[, liten := FALSE]
if (nrow(smaa)) base[smaa, liten := TRUE, on = c("gender", "hovedgruppe")]

prim_m <- base$kohort_primar & base$skaarbar & !base$liten

# ---- Standardisering: celleparametre fra primærutvalget ------------------------------------
pz <- base[prim_m]
for (kol in c("delta", "delta_max", "delta_all", "delta_vind", "delta_bg2", "delta_nk",
              "niva_w1")) {
  st <- pz[, .(mu = mean(get(kol), na.rm = TRUE), s = sd(get(kol), na.rm = TRUE)),
           by = .(gender, hovedgruppe)]
  st[s == 0, s := NA_real_]
  base[st, paste0(kol, "_z") := (get(kol) - i.mu) / i.s, on = c("gender", "hovedgruppe")]
}
for (v in c("vol1314", "vol1516")) {
  mu <- mean(pz[[v]]); s <- sd(pz[[v]])
  base[, paste0(v, "_g") := (get(v) - mu) / s]
}

prim <- base[prim_m & !is.na(delta_z) & !is.na(niva_w1_z)]
prim[, log_klubb_f := fifelse(is.na(log_klubb), median(prim$log_klubb, na.rm = TRUE), log_klubb)]
prim[, bk := factor(birth_year)]

fwrite(data.table(landmark = length(landmark),
                  landmark_med_kjonn = nrow(base),
                  uten_fodselsdato = sum(is.na(base$kvartal)),
                  landmark_1998_2005 = sum(base$kohort_primar),
                  uten_skaarbar = sum(base$kohort_primar & !base$skaarbar),
                  ekskl_smaacelle = sum(base$kohort_primar & base$skaarbar & base$liten),
                  n_prim_for_dropna = sum(prim_m),
                  n_prim_modeller = nrow(prim),
                  seniorer = sum(prim$senior)), "audit/r_out/utvalg.csv")

# Radvis kontroll mot analysedata (nøkkelvariablene)
ad <- fread("data_private/analysedata.csv")
adp <- ad[kohort_primar == TRUE & skaarbar == TRUE & liten_gruppecelle == FALSE]
mm <- merge(prim[, .(athlete_id, delta, niva_w1, vol1314, vol1516, k13, k15, senior)],
            adp[, .(athlete_id, p_delta = delta, p_niva = niva_w1, p_v13 = vol1314,
                    p_v15 = vol1516, p_k13 = k13, p_k15 = k15, p_sen = senior)],
            by = "athlete_id", all = TRUE)
fwrite(data.table(kun_R = sum(is.na(mm$p_delta)), kun_py = sum(is.na(mm$delta)),
                  max_diff_delta = max(abs(mm$delta - mm$p_delta), na.rm = TRUE),
                  max_diff_niva = max(abs(mm$niva_w1 - mm$p_niva), na.rm = TRUE),
                  ulik_vol = sum(mm$vol1314 != mm$p_v13 | mm$vol1516 != mm$p_v15, na.rm = TRUE),
                  ulik_k = sum(mm$k13 != mm$p_k13 | mm$k15 != mm$p_k15, na.rm = TRUE),
                  ulik_senior = sum(mm$senior != mm$p_sen, na.rm = TRUE)),
       "audit/r_out/radkontroll.csv")

# ---- Modeller -------------------------------------------------------------------------------
or_rader <- function(m, merk, n, hendelser) {
  s <- summary(m)$coefficients
  data.table(analyse = merk, variabel = rownames(s), OR = exp(s[, 1]),
             KI_lav = exp(s[, 1] - z975 * s[, 2]), KI_hoy = exp(s[, 1] + z975 * s[, 2]),
             p = s[, 4], n = n, hendelser = hendelser)
}
f_m0 <- senior ~ gender + bk + log_klubb_f
f_m1 <- update(f_m0, . ~ . + niva_w1_z + vol1314_g + vol1516_g + k13 + k15)
f_m2 <- update(f_m1, . ~ . + delta_z)
ut <- list()
ut$m0 <- or_rader(glm(f_m0, binomial, prim), "M0", nrow(prim), sum(prim$senior))
ut$m1 <- or_rader(glm(f_m1, binomial, prim), "M1", nrow(prim), sum(prim$senior))
ut$m2 <- or_rader(glm(f_m2, binomial, prim), "M2", nrow(prim), sum(prim$senior))

# H2
dq <- prim[!is.na(kvartal)]
dq[, kvartal_c := kvartal - 2.5][, dxq := delta_z * kvartal_c]
ut$h2 <- or_rader(glm(update(f_m2, . ~ . + kvartal_c + dxq), binomial, dq),
                  "H2_interaksjon", nrow(dq), sum(dq$senior))
ut$h2a <- or_rader(glm(f_m2, binomial, dq[kvartal <= 2]), "H2_strata_Q1-Q2",
                   nrow(dq[kvartal <= 2]), sum(dq[kvartal <= 2, senior]))
ut$h2b <- or_rader(glm(f_m2, binomial, dq[kvartal >= 3]), "H2_strata_Q3-Q4",
                   nrow(dq[kvartal >= 3]), sum(dq[kvartal >= 3, senior]))

# Mediering
ut$medu <- or_rader(glm(update(f_m1, . ~ . + kvartal_c), binomial, dq), "med_uten_delta",
                    nrow(dq), sum(dq$senior))
ut$medm <- or_rader(glm(update(f_m2, . ~ . + kvartal_c), binomial, dq), "med_med_delta",
                    nrow(dq), sum(dq$senior))
X <- cbind(1, dq$kvartal_c); yv <- dq$delta_z
bh <- solve(crossprod(X), crossprod(X, yv))
u <- as.vector(yv - X %*% bh)
grp <- fifelse(is.na(dq$club_id), "ukjent", as.character(dq$club_id))
meat <- Reduce(`+`, lapply(split(seq_len(nrow(X)), grp), function(i) {
  xu <- crossprod(X[i, , drop = FALSE], u[i]); xu %*% t(xu) }))
G <- uniqueN(grp); N <- nrow(X); K <- ncol(X)
V <- solve(crossprod(X)) %*% meat %*% solve(crossprod(X)) * G / (G - 1) * (N - 1) / (N - K)
ut$trend <- data.table(analyse = "delta_z_paa_kvartal", variabel = "kvartal_c",
                       OR = bh[2], KI_lav = bh[2] - z975 * sqrt(V[2, 2]),
                       KI_hoy = bh[2] + z975 * sqrt(V[2, 2]), p = NA, n = nrow(dq),
                       hendelser = NA)

# Nivåmoderasjon
di <- copy(prim)[, dxn := delta_z * niva_w1_z]
ut$ni <- or_rader(glm(update(f_m2, . ~ . + dxn), binomial, di), "nivainteraksjon",
                  nrow(di), sum(di$senior))
# Tertilgrenser med numpys lineære kvantil UTEN R-s heltallsfuzz: (n-1)*1/3 = 1268.9999999999998
# i flyttall, så grensen havner 1-2 ULP under en eksakt bundet verdi. R-s quantile(type=7) runder
# indeksen til 1269 og legger de tre grenseutøverne i lavere tertil (1270/1270/1268 mot 1269/1269/1270).
np_kvantil <- function(x, p) {
  # pandas Series.quantile -> np.percentile(100*q) -> q/100: 100*(1/3)/100 = 0.33333333333333326,
  # én ULP under 1/3; deretter numpy _compute_virtual_index (alpha = beta = 1)
  p <- (p * 100) / 100
  xs <- sort(x); n <- length(xs); idx <- n * p + (1 + p * (1 - 1 - 1)) - 1
  j <- floor(idx); h <- idx - j
  a <- xs[j + 1]; b <- xs[min(j + 2, n)]
  if (h >= 0.5) b - (b - a) * (1 - h) else a + (b - a) * h
}
br <- c(min(di$niva_w1_z), np_kvantil(di$niva_w1_z, 1/3), np_kvantil(di$niva_w1_z, 2/3),
        max(di$niva_w1_z))
di[, ntert := cut(niva_w1_z, br, include.lowest = TRUE, labels = c("lav", "midt", "hoy"))]
br_r <- quantile(di$niva_w1_z, c(0, 1/3, 2/3, 1), type = 7)
fwrite(data.table(konvensjon = c("numpy", "R_type7"),
                  lav = c(sum(di$ntert == "lav"), sum(cut(di$niva_w1_z, br_r, include.lowest = TRUE) == levels(cut(di$niva_w1_z, br_r, include.lowest = TRUE))[1])),
                  hoy = c(sum(di$ntert == "hoy"), sum(cut(di$niva_w1_z, br_r, include.lowest = TRUE) == levels(cut(di$niva_w1_z, br_r, include.lowest = TRUE))[3]))),
       "audit/r_out/tertilkonvensjon.csv")
for (t in c("lav", "midt", "hoy")) {
  g <- di[ntert == t]
  ut[[paste0("nt_", t)]] <- or_rader(glm(f_m2, binomial, g), paste0("nivastrata_", t),
                                     nrow(g), sum(g$senior))
}
di[, ntert_r := cut(niva_w1_z, br_r, include.lowest = TRUE, labels = c("lav", "midt", "hoy"))]
for (t in c("lav", "midt", "hoy")) {
  g <- di[ntert_r == t]
  ut[[paste0("ntR_", t)]] <- or_rader(glm(f_m2, binomial, g), paste0("nivastrata_Rkonv_", t),
                                      nrow(g), sum(g$senior))
}

# Kjønn
di[, kvinne := as.numeric(gender == "F")][, dxk := delta_z * kvinne]
ut$kji <- or_rader(glm(update(f_m2, . ~ . + dxk), binomial, di), "kjonnsinteraksjon",
                   nrow(di), sum(di$senior))
f_uk <- senior ~ bk + log_klubb_f + niva_w1_z + vol1314_g + vol1516_g + k13 + k15 + delta_z
for (kj in c("M", "F")) {
  g <- di[gender == kj]
  ut[[paste0("kj_", kj)]] <- or_rader(glm(f_uk, binomial, g), paste0("kjonnsstrata_", kj),
                                      nrow(g), sum(g$senior))
}

# Kvintiler (qcut på rank, type 7)
rk <- frank(di$delta_z, ties.method = "first")
brk <- quantile(rk, seq(0, 1, .2), type = 7)
di[, kv := cut(rk, brk, include.lowest = TRUE, labels = paste0("Q", 1:5))]
di[, `:=`(dq_Q2 = as.numeric(kv == "Q2"), dq_Q3 = as.numeric(kv == "Q3"),
          dq_Q4 = as.numeric(kv == "Q4"), dq_Q5 = as.numeric(kv == "Q5"))]
ut$kvint <- or_rader(glm(update(f_m1, . ~ . + dq_Q2 + dq_Q3 + dq_Q4 + dq_Q5), binomial, di),
                     "kvintiler", nrow(di), sum(di$senior))

# Fast vindu per kohorthalvdel
for (k in c("A", "B")) {
  g <- di[kohort == k]
  g[, bk := droplevels(bk)]
  m <- glm(update(f_m2, senior_20_21 ~ .), binomial, g)
  ut[[paste0("fv_", k)]] <- or_rader(m, paste0("fast_vindu_", k), nrow(g), sum(g$senior_20_21))
}

# Switcher (inklusiv bg2)
sw_base <- copy(base)
sw_base[, log_klubb_f := fifelse(is.na(log_klubb), median(base$log_klubb, na.rm = TRUE), log_klubb)]
sw_base[, bk := factor(birth_year)]
inkl <- sw_base[kohort_primar & !liten & !is.na(delta_bg2_z) & !is.na(niva_w1_z)]
m <- glm(senior ~ gender + bk + log_klubb_f + niva_w1_z + vol1314_g + vol1516_g
         + k13 + k15 + delta_bg2_z, binomial, inkl)
ut$sw <- or_rader(m, "switcher_inklusiv", nrow(inkl), sum(inkl$senior))

# Gruppekonsistent switcher-spesifikasjon: fremgang, nivå og antall i beste gruppe ved 15-16,
# standardisert innen kjønn × beste gruppe i det inklusive utvalget; celler med færre enn 20 ut
kons <- sw_base[kohort_primar & !is.na(delta_bg2)]
kons[, celle_n := .N, by = .(gender, bestgruppe)]
kons <- kons[celle_n >= 20]
kons[, `:=`(dz = (delta_bg2 - mean(delta_bg2)) / sd(delta_bg2),
            nz = (niva_w1_bg - mean(niva_w1_bg)) / sd(niva_w1_bg)), by = .(gender, bestgruppe)]
m <- glm(senior ~ gender + bk + log_klubb_f + nz + vol1314_g + vol1516_g + k13_bg + k15_bg + dz,
         binomial, kons)
ut$sw_kons <- or_rader(m, "switcher_konsistent", nrow(kons), sum(kons$senior))
fwrite(data.table(n = nrow(kons), hendelser = sum(kons$senior),
                  prim_i_modell = sum(kons$athlete_id %in% prim$athlete_id),
                  gjenvunnet_578 = sum(!kons$skaarbar),
                  gjenvunnet_smaa_celler = sum(kons$skaarbar & kons$liten),
                  ulik_gruppe = sum(kons$bestgruppe != kons$hovedgruppe)),
       "audit/r_out/switcher_konsistent.csv")

# Robusthet: eksponeringsvarianter, covid, k>=2, utfall, kohorter, klubbklynge
eksp_or <- function(dd, ekspo, merk, utfall = "senior") {
  dd <- dd[!is.na(get(ekspo))]
  f <- as.formula(paste(utfall, "~ gender + bk + log_klubb_f + niva_w1_z + vol1314_g",
                        "+ vol1516_g + k13 + k15 +", ekspo))
  or_rader(glm(f, binomial, dd), merk, nrow(dd), sum(dd[[utfall]]))[variabel == ekspo]
}
ut$e1 <- rbindlist(lapply(c("delta_z", "delta_max_z", "delta_all_z", "delta_vind_z",
                            "delta_bg2_z", "delta_nk_z"),
                          function(e) eksp_or(prim, e, paste0("eksvar_", e))))
ut$e2 <- eksp_or(prim[!birth_year %in% 2004:2005][, bk := droplevels(bk)], "delta_z", "uten_covid_kull")
k2 <- prim[k13 >= 2 & k15 >= 2]
ut$e3 <- eksp_or(k2, "delta_z", "k_minst_2")
ut$e4 <- eksp_or(prim, "delta_z", "utfall_min1", "senior_min1")
ut$e5 <- eksp_or(prim, "delta_z", "utfall_20_21", "senior_20_21")
a18 <- copy(base)[skaarbar & !liten & !is.na(delta_z) & !is.na(niva_w1_z)]
a18[, log_klubb_f := fifelse(is.na(log_klubb), median(prim$log_klubb, na.rm = TRUE), log_klubb)]
a18[, bk := factor(birth_year)]
ut$e6 <- eksp_or(a18, "delta_z", "aktiv18_inkl_2006", "aktiv18")
for (k in c("A", "B")) {
  g <- prim[kohort == k][, bk := droplevels(bk)]
  ut[[paste0("ek_", k)]] <- eksp_or(g, "delta_z", paste0("kohort_", k))
}
pc <- copy(prim)[, covid := as.numeric(birth_year %in% 2004:2006)][, dxc := delta_z * covid]
ut$cov <- or_rader(glm(update(f_m2, . ~ . + covid + dxc), binomial, pc), "covid_interaksjon",
                   nrow(pc), sum(pc$senior))

# ---- Revisjon r2 (audit 30.10.2026) ---------------------------------------------------------
suppressMessages({library(splines); library(fixest)})
setFixest_nthreads(1)   # flere tråder gir flyttallsstøy mellom kjøringer; én tråd gir like hasher
m3 <- function(x) mean(sort(x, decreasing = TRUE)[seq_len(min(3, length(x)))])
# like mange resultater: forventet snitt av tre beste over alle utvalg på n uten tilbakelegging;
# verdi nr. j (synkende) teller når den er med og færre enn min(3, n) høyere verdier er med
fm3 <- function(x, n) {
  x <- sort(x, decreasing = TRUE); k <- length(x); m <- min(3, n); i <- 0:(m - 1)
  p <- vapply(seq_len(k) - 1, function(j) sum(choose(j, i) * choose(k - 1 - j, n - 1 - i)), 0) / choose(k, n)
  sum(x * p) / m
}
lik_k <- function(a, b) { n <- min(length(a), length(b)); fm3(b, n) - fm3(a, n) }
std_prim <- function(dd, kol) {   # standardisering innen kjønn x gruppe over primærutvalget
  st <- dd[, .(mu = mean(get(kol), na.rm = TRUE), s = sd(get(kol), na.rm = TRUE)), by = .(gender, hovedgruppe)]
  dd[st, paste0(kol, "_z") := (get(kol) - i.mu) / i.s, on = c("gender", "hovedgruppe")]
}
hg_sc <- merge(sc[event_category == hovedgruppe], base[, .(athlete_id, gender)], by = "athlete_id")
l1 <- hg_sc[alder %in% 13:14, .(l = list(tyrving)), by = athlete_id]
l2 <- hg_sc[alder %in% 15:16, .(l = list(tyrving)), by = athlete_id]
ll <- merge(l1, l2, by = "athlete_id", suffixes = c("1", "2"))
ll <- ll[athlete_id %chin% prim$athlete_id][order(athlete_id)]
ll[, delta_lik := mapply(lik_k, l1, l2)]
pl <- merge(copy(prim), ll[, .(athlete_id, delta_lik)], by = "athlete_id", all.x = TRUE)
std_prim(pl, "delta_lik")
ut$r2_lik <- eksp_or(pl, "delta_lik_z", "r2_like_mange")
ut$r2_k3 <- eksp_or(prim[k13 >= 3 & k15 >= 3], "delta_z", "r2_k_minst_3")
ut$r2_a17 <- eksp_or(prim[siste_alder >= 17], "delta_z", "r2_aktiv_etter_16")
ms <- glm(senior ~ gender + bk + log_klubb_f + niva_w1_z + delta_z + bs(k13, df = 4) + bs(k15, df = 4)
          + bs(vol1314_g, df = 4) + bs(vol1516_g, df = 4), binomial, prim)
ut$r2_spl <- or_rader(ms, "r2_splines", nrow(prim), sum(prim$senior))[variabel == "delta_z"]
# bare utendørs og øvelsesjusterte poeng: Δ bygget på nytt fra poengradene (13-16)
me_i <- fread("data_private/meets.csv")[, .(meet_id = id, indoor)]
inne <- merge(r[, .(id, meet_id)], me_i, by = "meet_id")[tolower(as.character(indoor)) == "true", id]
d_fra <- function(s2, navn) {
  a <- s2[alder %in% 13:14, .(m1 = m3(tyrving)), by = athlete_id]
  b <- s2[alder %in% 15:16, .(m2 = m3(tyrving)), by = athlete_id]
  dd <- merge(copy(prim), merge(a, b, by = "athlete_id"), by = "athlete_id", all.x = TRUE)
  dd[, dx := m2 - m1]; std_prim(dd, "dx")
  eksp_or(dd, "dx_z", navn)
}
s16 <- hg_sc[alder <= 16 & athlete_id %chin% prim$athlete_id]
ut$r2_ute <- d_fra(s16[!(id %chin% inne)], "r2_bare_utendors")
s16[, celle := paste(athlete_id, alder)]
s16[, just := tyrving]
# forskyvningene er bare identifisert innen sett av øvelser som deler en utøversesong
# (guttekast: redskapene skifter ved 16); hvert sett beholder snittpoengene sine
sett_av <- function(ev, celle) {
  f <- setNames(sort(unique(ev)), sort(unique(ev)))
  rot <- function(e) { while (f[[e]] != e) e <- f[[e]]; e }
  for (u in split(ev, celle)) {
    u <- unique(u)
    for (e in u[-1]) { a <- rot(u[1]); b <- rot(e); if (a != b) f[[b]] <- a }
  }
  vapply(ev, rot, "")
}
for (gk in split(seq_len(nrow(s16)), paste(s16$gender, s16$hovedgruppe))) {
  g <- s16[gk]
  if (uniqueN(g$event_code) < 2) next
  fm <- feols(tyrving ~ factor(event_code) | celle, g, notes = FALSE, warn = FALSE)
  b <- coef(fm); b <- b[!is.na(b)]
  forsk <- setNames(rep(0, uniqueN(g$event_code)), sort(unique(g$event_code)))
  forsk[sub("factor\\(event_code\\)", "", names(b))] <- b
  fr <- unname(forsk[g$event_code])
  sett <- sett_av(g$event_code, g$celle)
  cat("øvelsessett", g$gender[1], g$hovedgruppe[1], uniqueN(sett), "\n")
  s16[gk, just := tyrving - (fr - ave(fr, sett))]
}
ut$r2_ovj <- d_fra(s16[, .(athlete_id, alder, tyrving = just)], "r2_ovelsesjustert")
# tidligere nivå gitt senere nivå
pn <- copy(prim)[!is.na(niva_w2)][, `:=`(l1 = niva_w1 / 100, l2 = niva_w2 / 100)]
ut$r2_l1l2 <- or_rader(glm(senior ~ gender + bk + log_klubb_f + vol1314_g + vol1516_g + k13 + k15 + l1 + l2,
                           binomial, pn), "r2_l1l2", nrow(pn), sum(pn$senior))[variabel %in% c("l1", "l2")]
# mediering: a-sti betinget på M1-kovariatene (klubbklynget) og kvartal i M0
klynge_ols <- function(X, yv, grp) {
  bh <- solve(crossprod(X), crossprod(X, yv)); u <- as.vector(yv - X %*% bh)
  meat <- Reduce(`+`, lapply(split(seq_len(nrow(X)), grp), function(i) {
    xu <- crossprod(X[i, , drop = FALSE], u[i]); xu %*% t(xu) }))
  G <- uniqueN(grp); N <- nrow(X); K <- ncol(X)
  V <- solve(crossprod(X)) %*% meat %*% solve(crossprod(X)) * G / (G - 1) * (N - 1) / (N - K)
  list(b = bh, V = V)
}
Xa <- model.matrix(~ gender + bk + log_klubb_f + niva_w1_z + vol1314_g + vol1516_g + k13 + k15 + kvartal_c, dq)
ka <- klynge_ols(Xa, dq$delta_z, grp); ia <- which(colnames(Xa) == "kvartal_c")
ut$r2_abet <- data.table(analyse = "r2_a_sti_betinget", variabel = "kvartal_c", OR = ka$b[ia],
                         KI_lav = ka$b[ia] - z975 * sqrt(ka$V[ia, ia]), KI_hoy = ka$b[ia] + z975 * sqrt(ka$V[ia, ia]),
                         p = NA, n = nrow(dq), hendelser = NA)
kn <- klynge_ols(cbind(1, dq$kvartal_c), dq$niva_w1_z, grp)
ut$r2_nivq <- data.table(analyse = "r2_niva_per_kvartal", variabel = "kvartal_c", OR = kn$b[2],
                         KI_lav = kn$b[2] - z975 * sqrt(kn$V[2, 2]), KI_hoy = kn$b[2] + z975 * sqrt(kn$V[2, 2]),
                         p = NA, n = nrow(dq), hendelser = NA)
ut$r2_tot <- or_rader(glm(senior ~ gender + bk + log_klubb_f + kvartal_c, binomial, dq), "r2_kvartal_M0",
                      nrow(dq), sum(dq$senior))[variabel == "kvartal_c"]
# nivåtertiler med k13 >= 3 og k15 >= 3 (tertilgrensene fra hele utvalget)
dk3 <- di[k13 >= 3 & k15 >= 3]
for (t in c("lav", "midt", "hoy")) {
  g <- dk3[ntert == t]
  ut[[paste0("r2_nt_", t)]] <- or_rader(glm(f_m2, binomial, g), paste0("r2_nivastrata_k3_", t),
                                        nrow(g), sum(g$senior))[variabel == "delta_z"]
}
ut$r2_nik3 <- or_rader(glm(update(f_m2, . ~ . + dxn), binomial, dk3), "r2_nivainteraksjon_k3",
                       nrow(dk3), sum(dk3$senior))[variabel == "dxn"]
fwrite(rbind(di[, .(utvalg = "alle", median_k15 = as.numeric(median(k15)), sd_delta_z = sd(delta_z)), by = ntert],
             dk3[, .(utvalg = "k_minst_3", median_k15 = as.numeric(median(k15)), sd_delta_z = sd(delta_z)), by = ntert]),
       "audit/r_out/nivatertiler.csv")
# kjønn i én modell: OR for menn og kvinner fra interaksjonsmodellen
mk <- glm(update(f_m2, . ~ . + dxk), binomial, di); bk_ <- coef(mk); Vk <- vcov(mk)
for (kj in c("menn", "kvinner")) {
  l <- if (kj == "menn") "delta_z" else c("delta_z", "dxk")
  e <- sum(bk_[l]); s <- sqrt(sum(Vk[l, l]))
  ut[[paste0("r2_kj_", kj)]] <- data.table(analyse = paste0("r2_kjonn_", kj), variabel = "delta_z", OR = exp(e),
                                          KI_lav = exp(e - z975 * s), KI_hoy = exp(e + z975 * s),
                                          p = summary(mk)$coefficients["dxk", 4], n = nrow(di), hendelser = NA)
}
# exit-justerte baner: ujustert, sesongmedian og like mange resultater
ex <- copy(prim)[, aktiv_naa := (birth_year + siste_alder) >= 2025][!aktiv_naa & siste_alder %between% c(16, 19)]
ex <- ex[order(athlete_id)]
lis <- hg_sc[, .(l = list(tyrving)), by = .(athlete_id, alder)]
setkey(lis, athlete_id, alder)
eb <- rbindlist(lapply(seq_len(nrow(ex)), function(i) {
  a <- ex$athlete_id[i]; aldre <- ex$siste_alder[i] - 3:0
  if (aldre[1] < 13) return(NULL)
  L <- lapply(aldre, function(x) { rr <- lis[.(a, x), nomatch = NULL]; if (nrow(rr)) rr$l[[1]] else NULL })
  if (any(vapply(L, is.null, logical(1)))) return(NULL)
  data.table(t = c("T-3", "T-2", "T-1", "T-0"), raa = sapply(L, m3) - m3(L[[1]]),
             med = sapply(L, median) - median(L[[1]]), lik = sapply(L, function(x) lik_k(L[[1]], x)),
             k = lengths(L))
}))
fwrite(eb[, .(n = .N, raa = median(raa), med = median(med), lik = median(lik), k = median(k)), by = t],
       "audit/r_out/exit_baner.csv")
# volumbanen: konkurransedager (alle øvelser) i alle fire sesonger
dg <- r[alder %between% c(13, 19), .(dager = uniqueN(date)), by = .(athlete_id, alder)]
setkey(dg, athlete_id, alder)
evol <- rbindlist(lapply(seq_len(nrow(ex)), function(i) {
  aldre <- ex$siste_alder[i] - 3:0
  if (aldre[1] < 13) return(NULL)
  d <- dg[.(ex$athlete_id[i], aldre)]$dager
  if (anyNA(d)) return(NULL)
  data.table(t = c("T-3", "T-2", "T-1", "T-0"), dager = d - d[1])
}))
fwrite(evol[, .(n = .N, dager = median(dager), n_kandidater = nrow(ex)), by = t], "audit/r_out/exit_volum.csv")
fwrite(pl[, .(median_lik = median(delta_lik, na.rm = TRUE), andel_neg_lik = mean(delta_lik < 0, na.rm = TRUE)),
          by = senior], "audit/r_out/delta_lik.csv")
fwrite(pl[, .(athlete_id, k13, k15, delta_lik)], "data_private/r_delta_lik_rader.csv")   # radnivå: ikke i git

fwrite(rbindlist(ut, fill = TRUE), "audit/r_out/logit.csv")

# Cox landmark fra 17
cx <- copy(prim)[siste_alder >= 17]   # landmark: bare de som er under risiko etter 16-årssesongen
cx[, aktiv_naa := (birth_year + siste_alder) >= 2025]
cx[, tid := siste_alder - 16]
cx[, hendelse := as.integer(!aktiv_naa)]
cx[, kvinne := as.numeric(gender == "F")]
cm <- coxph(Surv(tid, hendelse) ~ delta_z + niva_w1_z + vol1314_g + vol1516_g + k13 + k15 + kvinne,
            data = cx)
s <- summary(cm)$coefficients
fwrite(data.table(variabel = rownames(s), HR = exp(s[, 1]),
                  KI_lav = exp(s[, 1] - z975 * s[, 3]), KI_hoy = exp(s[, 1] + z975 * s[, 3])),
       "audit/r_out/cox.csv")

# E-verdi
h1or <- ut$e1[variabel == "delta_z", OR]
h1lo <- ut$e1[variabel == "delta_z", KI_lav]
p0 <- mean(prim$senior)
# vanlig utfall: RR ≈ √OR (VanderWeele og Ding 2017)
ev <- function(o) { rr <- sqrt(o); if (rr < 1) rr <- 1 / rr; rr + sqrt(rr * (rr - 1)) }
fwrite(data.table(p0 = p0, E_punkt = ev(h1or), E_grense = ev(h1lo)), "audit/r_out/everdi.csv")

# SD-er og andeler
pr <- base[prim_m]
fwrite(data.table(
  sd_delta = sd(pr$delta, na.rm = TRUE),
  sd_delta_min = min(pr[, sd(delta, na.rm = TRUE), by = .(gender, hovedgruppe)]$V1, na.rm = TRUE),
  sd_delta_max = max(pr[, sd(delta, na.rm = TRUE), by = .(gender, hovedgruppe)]$V1, na.rm = TRUE),
  sd_niva = sd(pr$niva_w1, na.rm = TRUE),
  sd_v1314 = sd(pr$vol1314), sd_v1516 = sd(pr$vol1516),
  neg_drop = mean(pr[senior == 0, delta] < 0, na.rm = TRUE),
  neg_ret = mean(pr[senior == 1, delta] < 0, na.rm = TRUE),
  q1 = sum(pr$kvartal == 1, na.rm = TRUE) / sum(!is.na(pr$kvartal)),
  q4 = sum(pr$kvartal == 4, na.rm = TRUE) / sum(!is.na(pr$kvartal))),
  "audit/r_out/sd_andeler.csv")

cat("uavhengig A1 ferdig\n")
