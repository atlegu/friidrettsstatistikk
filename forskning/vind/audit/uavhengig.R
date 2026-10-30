# uavhengig.R — A6 «Vind»: uavhengig reimplementasjon i R (audit fase 3).
# Skrevet fra metodeteksten (manus §2) og ANALYSEPLAN §3-4, ikke oversatt fra Python.
# Der teksten er taus (rimelighetsgrenser, måned 4-10, topp-5 runder, n>=300/celler>=100)
# følges den committede koden; avvikene er dokumentert i DATA_AUDIT.md.
# Output: audit/r_out/*.csv — sammenlignes mot tables/estimering/r1_* av sammenlign.py.

suppressMessages({library(data.table); library(fixest)})
setFixest_nthreads(1)   # flere tråder ga avvik på 1e-13 mellom kjøringer (se også stevne-FE nedenfor)
setwd(dirname(dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])))))
dir.create("audit/r_out", showWarnings = FALSE)

TID <- c("60m", "80m", "100m", "150m", "200m")
GRENSER <- list("60m" = c(6.4, 16), "80m" = c(8.5, 20), "100m" = c(9.5, 22),
                "150m" = c(14, 35), "200m" = c(19, 45),
                "lengde" = c(1.0, 8.6), "lengde_sone_05m" = c(1.0, 8.6),
                "tresteg" = c(4.0, 18.5), "tresteg_sone_05m" = c(4.0, 18.5))
band_av <- function(a) fcase(a <= 11, "10-11", a <= 13, "12-13", a <= 15, "14-15",
                             a <= 17, "16-17", a <= 19, "18-19", default = "20-34")

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

bygg <- function(resfil, koder_tid_alle = FALSE) {
  r <- fjern_kopier(fread(resfil))
  utv <- fread("data_private/utovere.csv"); setnames(utv, "id", "athlete_id")
  me <- fread("data_private/meets.csv"); setnames(me, "id", "meet_id")
  d <- merge(r, utv, by = "athlete_id", all.x = TRUE)
  d <- merge(d, me[, .(meet_id, indoor)], by = "meet_id", all.x = TRUE)
  d[, date := as.IDate(date)][, aar := year(date)][, maaned := month(date)]
  d <- d[status == "OK"]
  d <- d[!(tolower(as.character(indoor)) %in% "true")]
  d <- d[!(tolower(as.character(is_manual_time)) %in% "true")]
  d <- d[gender %chin% c("M", "F") & !is.na(birth_year)]
  d[, alder := aar - birth_year]
  d <- d[alder >= 10 & alder <= 34]
  # 2026: sonehopp lå under brettkoden (feil kode, ikke kopier) -> brettkodede hopp ved 11-13 ut
  d <- d[!(aar == 2026 & event_code %chin% c("lengde", "tresteg") & alder >= 11 & alder <= 13)]
  d <- d[!is.na(wind) & abs(wind) <= 8]
  if (koder_tid_alle) {
    d[, y := performance_value / 100]
    dist <- tstrsplit(d$event_code, "_")[[1]]
    gr_lo <- c("60mh" = 7.5, "80mh" = 10, "100mh" = 12, "110mh" = 13)
    gr_hi <- c("60mh" = 20, "80mh" = 26, "100mh" = 32, "110mh" = 34)
    d <- d[y >= gr_lo[dist] & y <= gr_hi[dist]]
  } else {
    d[, med_pv := median(performance_value, na.rm = TRUE), by = event_code]
    d[, y := fifelse(event_code %chin% TID, performance_value / 100,
                     fifelse(med_pv > 1500, performance_value / 1000, performance_value / 100))]
    lov <- sapply(GRENSER, `[`, 1); hov <- sapply(GRENSER, `[`, 2)
    d <- d[y >= lov[event_code] & y <= hov[event_code]]
  }
  d[, aldersband := band_av(alder)]
  d[, celle := paste(athlete_id, aar, event_code, sep = "_")]
  d[, n_i_celle := .N, by = celle]
  d[, runde := fifelse(is.na(round) | round == "", "ukjent", as.character(round))]
  d[, round := NULL]
  d
}

# ---- Estimering: within utøver x sesong, måned- og rundedummyer, stevneklynget ---------
# Småutvalgskorreksjon som fixest-standard: absorberte celler telles når de ikke er nøstet i
# stevneklyngene (audit 30.10.2026, funn A6-7); med fe2 = TRUE også stevne-FE (nøstet, telles ikke)
est <- function(dd, ykol = "y", vind = "wind", min_n = 300, min_celler = 100, fe2 = FALSE) {
  dd <- dd[n_i_celle >= 2]
  if (nrow(dd) < min_n || uniqueN(dd$celle) < min_celler) return(NULL)
  dd <- copy(dd)
  dd[, mnd := pmin(pmax(maaned, 4), 10)]
  topp <- names(sort(table(dd$runde), decreasing = TRUE))[seq_len(min(5, uniqueN(dd$runde)))]
  dd[, rnd := fifelse(runde %chin% topp, runde, "annet")]
  fml <- as.formula(paste(ykol, "~", paste(vind, collapse = " + "),
                          "+ factor(mnd) + factor(rnd) | celle", if (fe2) " + meet_id" else ""))
  m <- feols(fml, data = dd, vcov = cluster ~ meet_id,
             ssc = ssc(adj = TRUE, fixef.K = "nested", cluster.adj = TRUE))
  list(m = m, n = nrow(dd), celler = uniqueN(dd$celle))
}

rad <- function(res, kode, vind = "wind") {
  if (is.null(res)) return(NULL)
  b <- coef(res$m)[vind]; se <- sqrt(diag(vcov(res$m)))[vind]
  s <- if (kode %in% TID) -1 else 1
  sk <- if (kode %in% TID) 1 else 100
  data.table(event = kode, gevinst = s * b * sk,
             ki_lav = s * b * sk - qnorm(.975) * se * sk,
             ki_hoy = s * b * sk + qnorm(.975) * se * sk,
             n = res$n, celler = res$celler)
}

d <- bygg("data_private/resultater.csv")

# Utvalgskontroll: per øvelse og multisett-nøkkel mot analyseklar.csv
ak <- fread("data_private/analyseklar.csv")
u1 <- d[, .(r_rader = .N, r_min2 = sum(n_i_celle >= 2), r_celler2 = uniqueN(celle[n_i_celle >= 2])), by = event_code][order(event_code)]
u2 <- ak[, .(ak_rader = .N, ak_min2 = sum(n_i_celle >= 2)), by = event_code][order(event_code)]
fwrite(merge(u1, u2, by = "event_code"), "audit/r_out/utvalg_per_ovelse.csv")
k1 <- d[, .(n_r = .N), by = .(athlete_id, meet_id, event_code, aar, y = round(y, 4), wind)]
k2 <- ak[, .(n_ak = .N), by = .(athlete_id, meet_id, event_code, aar, y = round(y, 4), wind)]
mk <- merge(k1, k2, all = TRUE)
mk[is.na(n_r), n_r := 0L][is.na(n_ak), n_ak := 0L]
fwrite(data.table(avvikende_nokler = nrow(mk[n_r != n_ak]),
                  rader_kun_R = sum(mk[n_ak == 0, n_r]), rader_kun_ak = sum(mk[n_r == 0, n_ak])),
       "audit/r_out/utvalg_multisett.csv")

d[, logy := log(y)]
d[, wind_pos := pmax(wind, 0)][, wind_neg := pmin(wind, 0)]

# ---- Hoved + prosent per øvelse ---------------------------------------------------------
hov <- rbindlist(lapply(sort(unique(d$event_code)), function(k) {
  a <- rad(est(d[event_code == k]), k)
  if (!is.null(a)) a[, analyse := "hoved"]
  p <- est(d[event_code == k], "logy")
  if (!is.null(p)) {
    b <- coef(p$m)["wind"]; se <- sqrt(diag(vcov(p$m)))["wind"]
    s <- if (k %in% TID) -1 else 1
    a <- rbind(a, data.table(event = k, gevinst = s * 100 * b,
                             ki_lav = s * 100 * b - qnorm(.975) * 100 * se,
                             ki_hoy = s * 100 * b + qnorm(.975) * 100 * se,
                             n = p$n, celler = p$celler, analyse = "pst"))
  }
  a
}))
fwrite(hov, "audit/r_out/hoved.csv")

# ---- Alder x kjønn (naturlig enhet og %) --------------------------------------------------
ald <- rbindlist(lapply(c("60m", "100m", "200m", "lengde", "lengde_sone_05m", "tresteg"),
  function(k) rbindlist(lapply(c("M", "F"), function(kj)
  rbindlist(lapply(unique(d[event_code == k & gender == kj, aldersband]), function(b) {
    g <- d[event_code == k & gender == kj & aldersband == b]
    a <- rad(est(g), k)
    if (!is.null(a)) a[, `:=`(kjonn = kj, aldersband = b, enhet = fifelse(k %chin% TID, "s", "cm"))]
    p <- est(g, "logy")
    if (!is.null(p)) {
      bb <- coef(p$m)["wind"]; se <- sqrt(diag(vcov(p$m)))["wind"]
      s <- if (k %in% TID) -1 else 1
      a <- rbind(a, data.table(event = k, gevinst = s * 100 * bb,
                               ki_lav = s * 100 * bb - qnorm(.975) * 100 * se,
                               ki_hoy = s * 100 * bb + qnorm(.975) * 100 * se,
                               n = p$n, celler = p$celler, kjonn = kj, aldersband = b,
                               enhet = "%"), fill = TRUE)
    }
    a
  }), fill = TRUE)), fill = TRUE)), fill = TRUE)
fwrite(ald, "audit/r_out/alder.csv")

# ---- Asymmetri per øvelse ---------------------------------------------------------------
asy <- rbindlist(lapply(sort(unique(d$event_code)), function(k) {
  r <- est(d[event_code == k], vind = c("wind_pos", "wind_neg"))
  if (is.null(r)) return(NULL)
  b <- coef(r$m); V <- vcov(r$m)
  s <- if (k %in% TID) -1 else 1; sk <- if (k %in% TID) 1 else 100
  dif <- b["wind_pos"] - b["wind_neg"]
  sed <- sqrt(V["wind_pos", "wind_pos"] + V["wind_neg", "wind_neg"] - 2 * V["wind_pos", "wind_neg"])
  ut <- data.table(event = k,
             medvind = s * b["wind_pos"] * sk, motvind = s * b["wind_neg"] * sk,
             med_se = sqrt(V["wind_pos", "wind_pos"]) * sk, mot_se = sqrt(V["wind_neg", "wind_neg"]) * sk,
             p_lik = 2 * (1 - pnorm(abs(dif / sed))), n = r$n)
  # Drag-referanse for samme estimator: ren drag-fysikk på de observerte vindene (A6-1)
  if (k %chin% c("60m", "100m", "200m")) {
    g <- copy(d[event_code == k])
    lengde <- c("60m" = 60, "100m" = 100, "200m" = 200)[[k]]
    g[, tm := mean(y), by = celle][, v := lengde / tm]
    g[, ysim := tm * ((v - wind)^2 - v^2) / v^2][, wind2 := wind^2]
    cc <- coef(est(g)$m)["wind"] / coef(est(g, "ysim")$m)["wind"]
    ps <- coef(est(g, "ysim", vind = c("wind_pos", "wind_neg"))$m)
    qs <- coef(est(g, "ysim", vind = c("wind", "wind2"))$m)
    ut[, `:=`(ratio_drag = ps["wind_neg"] / ps["wind_pos"], drag_medvind = -cc * ps["wind_pos"],
              drag_motvind = -cc * ps["wind_neg"], drag_kvad = cc * qs["wind2"])]
  }
  ut
}), fill = TRUE)
fwrite(asy, "audit/r_out/asym.csv")

# ---- Lybbert & Zheng (2023): motvind/medvind på 100 m per kjønn og alder mot drag ved egen fart ----
dr_forhold <- function(g, fe2 = FALSE, fast_tid = NULL) {
  g <- copy(g)
  if (is.null(fast_tid)) g[, tm := mean(y), by = celle] else g[, tm := fast_tid]
  g[, v := 100 / tm][, ysim := tm * ((v - wind)^2 - v^2) / v^2]
  b <- coef(est(g, "ysim", vind = c("wind_pos", "wind_neg"), fe2 = fe2)$m)
  unname(b["wind_neg"] / b["wind_pos"])
}
lz_rad <- function(g, kj, band, fe2) {
  r <- est(g, vind = c("wind_pos", "wind_neg"), fe2 = fe2)
  if (is.null(r)) return(NULL)
  b <- coef(r$m); V <- vcov(r$m)
  R <- unname(b["wind_neg"] / b["wind_pos"])
  se <- abs(R) * sqrt(V["wind_neg", "wind_neg"] / b["wind_neg"]^2 + V["wind_pos", "wind_pos"] / b["wind_pos"]^2
                      - 2 * V["wind_neg", "wind_pos"] / (b["wind_neg"] * b["wind_pos"]))
  data.table(kjonn = kj, aldersband = band, stevne_fe = fe2, n = r$n, medvind_s = -unname(b["wind_pos"]),
             motvind_s = -unname(b["wind_neg"]), forhold = R, ki_lav = R - 1.96 * se, ki_hoy = R + 1.96 * se,
             forhold_drag = dr_forhold(g, fe2))
}
d100 <- d[event_code == "100m"]
lz <- rbindlist(c(
  lapply(split(d100, by = c("gender", "aldersband")), function(g) lz_rad(g, g$gender[1], g$aldersband[1], FALSE)),
  lapply(split(d100, by = "gender"), function(g) lz_rad(g, g$gender[1], "alle", FALSE)),
  lapply(split(d100, by = "gender"), function(g) lz_rad(g, g$gender[1], "alle", TRUE))), fill = TRUE)
num <- names(lz)[vapply(lz, is.double, logical(1))]
lz[, (num) := lapply(.SD, signif, 10), .SDcols = num]   # toveis FE: maskinpresisjonsstøy (se stevne-FE)
fwrite(lz, "audit/r_out/lz_asym.csv")
fart <- data.table(gruppe = c("elite_menn", "us_hs_gutter", "us_hs_jenter"), tid_s = c(10.0, 12.603, 14.557))
fart[, forhold_drag := sapply(tid_s, function(tt) dr_forhold(d100, FALSE, tt))]
fwrite(fart, "audit/r_out/lz_fart.csv")

# ---- Kvadratisk form (rå enheter: s for løp, m for hopp), stevneklynget -----------------
d[, wind2 := wind^2]
kv <- rbindlist(lapply(sort(unique(d$event_code)), function(k) {
  r <- est(d[event_code == k], vind = c("wind", "wind2"))
  if (is.null(r)) return(NULL)
  b <- coef(r$m); se <- sqrt(diag(vcov(r$m)))
  data.table(event = k, beta_lin = b["wind"], se_lin = se["wind"],
             beta_kvad = b["wind2"], se_kvad = se["wind2"], n = r$n)
}))
fwrite(kv, "audit/r_out/kvad.csv")

# ---- Vindu: begge grener per bånd (60/100/200) + poolet justert SD ----------------------
beta_h <- setNames(hov[analyse == "hoved", gevinst], hov[analyse == "hoved", event])
d[, y_adj := fifelse(event_code %chin% TID, y + beta_h[event_code] * wind,
                     y - beta_h[event_code] / 100 * wind)]
d[, cm_adj := mean(y_adj), by = celle]
d[, res2 := (y_adj - cm_adj)^2]
vin <- rbindlist(lapply(c("60m", "100m", "200m"), function(k) rbindlist(lapply(c("M", "F"), function(kj)
  rbindlist(lapply(unique(d[event_code == k & gender == kj, aldersband]), function(b) {
    g <- d[event_code == k & gender == kj & aldersband == b]
    r <- est(g, vind = c("wind_pos", "wind_neg"))
    if (is.null(r)) return(NULL)
    bb <- coef(r$m); V <- vcov(r$m)
    g3 <- g[n_i_celle >= 3]
    frih <- max(sum(g3[, .N, by = celle]$N - 1), 1)
    sdp <- sqrt(sum(g3$res2) / frih)
    # Verdien av +2,0 fra helningen over 0..+2 (knekk ved 0 og +2) og robust skala (MAD) (A6-4/5)
    g02 <- copy(g)[, `:=`(w02 = pmin(pmax(wind, 0), 2), w2p = pmax(wind - 2, 0))]
    b02 <- coef(est(g02, vind = c("w02", "w2p", "wind_neg"))$m)["w02"]
    rob <- mad(g3$y_adj - g3$cm_adj) * sqrt(nrow(g3) / frih)
    data.table(event = k, kjonn = kj, aldersband = b,
               medvind = -bb["wind_pos"], med_se = sqrt(V["wind_pos", "wind_pos"]),
               motvind = -bb["wind_neg"], mot_se = sqrt(V["wind_neg", "wind_neg"]),
               fordel_2ms = -2 * bb["wind_pos"], sd_pool = sdp,
               fordel_i_sd = -2 * bb["wind_pos"] / sdp,
               fordel_0_2 = -2 * b02, skala_robust = rob, fordel_0_2_robust = -2 * b02 / rob, n = r$n)
  }))))), fill = TRUE)
fwrite(vin, "audit/r_out/vindu.csv")

# ---- Stevne-FE per kjønn og aldersbånd (tabell S6) ---------------------------------------
fe <- rbindlist(lapply(c("60m", "100m", "200m"), function(k) rbindlist(lapply(c("M", "F"), function(kj)
  rbindlist(lapply(unique(d[event_code == k & gender == kj, aldersband]), function(b) {
    g <- d[event_code == k & gender == kj & aldersband == b]
    r <- est(g, fe2 = TRUE)
    if (is.null(r)) return(NULL)
    bb <- coef(r$m)["wind"]; se <- sqrt(vcov(r$m)["wind", "wind"])
    data.table(event = k, kjonn = kj, aldersband = b, stevne_fe = -bb,
               ki_lav = -bb - qnorm(.975) * se, ki_hoy = -bb + qnorm(.975) * se, n = r$n)
  }))))), fill = TRUE)
# toveis FE gir maskinpresisjonsstøy (1e-16) mellom R-prosesser selv med én tråd; avrund før
# skriving så filen får samme hash ved hver kjøring (sammenlign.py har toleranser >= 1e-6)
num <- names(fe)[vapply(fe, is.double, logical(1))]
fe[, (num) := lapply(.SD, signif, 10), .SDcols = num]
fwrite(fe, "audit/r_out/stevne_fe_alder.csv")

# ---- Evnetertiler av utøversesonger (celler >= 2), vindjustert cellesnitt ----------------
cel <- d[n_i_celle >= 2, .(cm = mean(y_adj)), by = .(celle, event_code, gender, aldersband)]
cel[, prest := fifelse(event_code %chin% TID, -cm, cm)]
setorder(cel, event_code, gender, aldersband, prest, celle)
cel[, rang := seq_len(.N), by = .(event_code, gender, aldersband)]
cel[, m := .N, by = .(event_code, gender, aldersband)]
cel[, tert := fifelse(m >= 30, c("lav", "midt", "hoy")[floor(3 * (rang - 1) / m) + 1], NA_character_)]
d[cel, tert := i.tert, on = "celle"]
ter <- rbindlist(lapply(sort(unique(d$event_code)), function(k) rbindlist(lapply(c("lav", "midt", "hoy"),
  function(t) { a <- rad(est(d[event_code == k & tert == t]), k); if (!is.null(a)) a[, tertil := t]; a }))))
fwrite(ter, "audit/r_out/tertil.csv")

# ---- Deskriptive størrelser: bunching, per sekund, manglende vind, innendørsrader --------
w <- d$wind
fwrite(data.table(i16_18 = mean(w >= 1.6 & w <= 1.8), i18_20 = mean(w > 1.8 & w <= 2.0),
                  i20_22 = mean(w > 2.0 & w <= 2.2), i22_24 = mean(w > 2.2 & w <= 2.4),
                  null = mean(w == 0), to = mean(w == 2.0)), "audit/r_out/bunching.csv")
fwrite(d[event_code %chin% TID, .(snitt = mean(y)), by = event_code][
  , per_sekund := beta_h[event_code] / snitt], "audit/r_out/per_sekund.csv")
r0 <- fjern_kopier(fread("data_private/resultater.csv",
                         select = c("id", "athlete_id", "date", "performance_value", "round",
                                    "event_code", "meet_id", "wind", "status")))
me0 <- fread("data_private/meets.csv"); setnames(me0, "id", "meet_id")
r0 <- merge(r0, me0[, .(meet_id, indoor)], by = "meet_id", all.x = TRUE)
ute <- r0[status == "OK" & !(tolower(as.character(indoor)) %in% "true")]
ute[, str := .N, by = meet_id]
br_s <- quantile(ute$str, c(0, 1/3, 2/3, 1), type = 7)
ute[, str_t := cut(str, unique(br_s), include.lowest = TRUE, labels = FALSE)]
fwrite(rbind(data.table(gruppe = "alle_ute", andel = mean(is.na(ute$wind)), n = nrow(ute),
                        mangler = sum(is.na(ute$wind))),
             ute[, .(andel = mean(is.na(wind)), n = .N, mangler = sum(is.na(wind))),
                 by = .(gruppe = paste0("str_tertil_", str_t))]),
       "audit/r_out/manglende_vind.csv")
fwrite(r0[tolower(as.character(indoor)) %in% "true", .N, by = event_code],
       "audit/r_out/innendors.csv")

# ---- Hekk per kode ----------------------------------------------------------------------
h <- bygg("data_private/resultater_hekk.csv", koder_tid_alle = TRUE)
hk <- rbindlist(lapply(sort(unique(h$event_code)), function(k) rbindlist(lapply(c("begge", "M", "F"), function(kj) {
  g <- if (kj == "begge") h[event_code == k] else h[event_code == k & gender == kj]
  r <- est(g)
  if (is.null(r)) return(NULL)
  b <- coef(r$m)["wind"]; se <- sqrt(diag(vcov(r$m)))["wind"]
  data.table(kode = k, kjonn = kj, gevinst = -b,
             ki_lav = -b - qnorm(.975) * se, ki_hoy = -b + qnorm(.975) * se,
             snitt_tid = mean(g$y), n = r$n, celler = r$celler)
}))), fill = TRUE)
fwrite(hk, "audit/r_out/hekk.csv")

cat("uavhengig A6 ferdig\n")
