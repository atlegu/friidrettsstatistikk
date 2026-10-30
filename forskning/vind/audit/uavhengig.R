# uavhengig.R — A6 «Vind»: uavhengig reimplementasjon i R (audit fase 3).
# Skrevet fra metodeteksten (manus §2) og ANALYSEPLAN §3-4, ikke oversatt fra Python.
# Der teksten er taus (rimelighetsgrenser, måned 4-10, topp-5 runder, n>=300/celler>=100)
# følges den committede koden; avvikene er dokumentert i DATA_AUDIT.md.
# Output: audit/r_out/*.csv — sammenlignes mot tables/estimering/r1_* av sammenlign.py.

suppressMessages({library(data.table); library(fixest)})
setwd(dirname(dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])))))
dir.create("audit/r_out", showWarnings = FALSE)

TID <- c("60m", "80m", "100m", "150m", "200m")
GRENSER <- list("60m" = c(6.4, 16), "80m" = c(8.5, 20), "100m" = c(9.5, 22),
                "150m" = c(14, 35), "200m" = c(19, 45),
                "lengde" = c(1.0, 8.6), "lengde_sone_05m" = c(1.0, 8.6),
                "tresteg" = c(4.0, 18.5), "tresteg_sone_05m" = c(4.0, 18.5))
band_av <- function(a) fcase(a <= 11, "10-11", a <= 13, "12-13", a <= 15, "14-15",
                             a <= 17, "16-17", a <= 19, "18-19", default = "20-34")

bygg <- function(resfil, koder_tid_alle = FALSE) {
  r <- fread(resfil)
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
est <- function(dd, ykol = "y", vind = "wind", min_n = 300, min_celler = 100) {
  dd <- dd[n_i_celle >= 2]
  if (nrow(dd) < min_n || uniqueN(dd$celle) < min_celler) return(NULL)
  dd <- copy(dd)
  dd[, mnd := pmin(pmax(maaned, 4), 10)]
  topp <- names(sort(table(dd$runde), decreasing = TRUE))[seq_len(min(5, uniqueN(dd$runde)))]
  dd[, rnd := fifelse(runde %chin% topp, runde, "annet")]
  fml <- as.formula(paste(ykol, "~", paste(vind, collapse = " + "),
                          "+ factor(mnd) + factor(rnd) | celle"))
  m <- feols(fml, data = dd, vcov = cluster ~ meet_id,
             ssc = ssc(adj = TRUE, fixef.K = "none", cluster.adj = TRUE))
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
  data.table(event = k,
             medvind = s * b["wind_pos"] * sk, motvind = s * b["wind_neg"] * sk,
             med_se = sqrt(V["wind_pos", "wind_pos"]) * sk, mot_se = sqrt(V["wind_neg", "wind_neg"]) * sk,
             p_lik = 2 * (1 - pnorm(abs(dif / sed))), n = r$n)
}))
fwrite(asy, "audit/r_out/asym.csv")

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
    data.table(event = k, kjonn = kj, aldersband = b,
               medvind = -bb["wind_pos"], med_se = sqrt(V["wind_pos", "wind_pos"]),
               motvind = -bb["wind_neg"], mot_se = sqrt(V["wind_neg", "wind_neg"]),
               fordel_2ms = -2 * bb["wind_pos"], sd_pool = sdp,
               fordel_i_sd = -2 * bb["wind_pos"] / sdp, n = r$n)
  }))))), fill = TRUE)
fwrite(vin, "audit/r_out/vindu.csv")

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
r0 <- fread("data_private/resultater.csv", select = c("event_code", "meet_id", "wind", "status"))
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
