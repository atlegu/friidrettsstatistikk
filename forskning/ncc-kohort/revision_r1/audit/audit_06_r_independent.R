# audit_06_r_independent.R - independent re-implementation in R (paper-data-audit, phase 3).
#
# Rebuilds the analysis variables from the raw career and cohort files, following the rules in
# the Methods (not the Python code), compares them row by row with the analysis file, and
# re-estimates the central models from the R-built variables. Tyrving scores are taken from
# r1_variables.csv: they are validated separately against the federation's workbook (1,596 of
# 1,596, audit_03) and by an independent Python scorer.
#
# Rules (Methods 2.2-2.5):
#   age = calendar year - birth year; meets at an age = distinct dates with a result;
#   active season = calendar year with >= 2 results; final active season = last active season
#   (baseline year if none); senior status = final active season at age >= 20;
#   active in 2024+ = final active season >= 2024; HHI = sum of squared category shares of the
#   results at ages 13-14; continuous covariates z-standardized over the cohort.
#
# Usage: Rscript audit_06_r_independent.R <folder with corrected/ and r1_variables.csv> <r1_results.json>
# Writes audit_06_summary.csv next to this script. No athlete-level output.

suppressMessages({library(data.table); library(survival); library(sandwich); library(lmtest); library(jsonlite)})
args <- commandArgs(trailingOnly = TRUE)
dir <- if (length(args) >= 1) args[1] else "../data_private"
res_json <- if (length(args) >= 2) args[2] else "../tables/r1_results.json"
here <- dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE))))

kar <- fread(file.path(dir, "corrected", "karrieredata_utvidet.csv"), select = c("id", "athlete_id", "date", "event_category"))
koh <- fread(file.path(dir, "corrected", "kohort_utvidet.csv"), select = c("athlete_id", "gender", "birth_year", "forste_utgave"))
ana <- fread(file.path(dir, "corrected", "analysedata_utvidet.csv"))
r1v <- fread(file.path(dir, "r1_variables.csv"), select = c("athlete_id", "tyrving_best_r1", "hhi_13_14"))
RES <- fromJSON(res_json)
out <- list()
add <- function(check, value) out[[length(out) + 1]] <<- data.table(check = check, value = as.character(value))

# ---------------------------------------------------------------- variables from the raw files
kar[, year := as.integer(substr(date, 1, 4))]
kar <- merge(kar, koh[, .(athlete_id, birth_year)], by = "athlete_id")
kar[, age := year - birth_year]
edition_year <- c(ncc_2011 = 2011, ncc_2012 = 2012, peab_2013 = 2013, peab_2014 = 2014, bendit_2015 = 2015, ungdomslekene_2016 = 2016)
koh[, base_year := edition_year[forste_utgave]]

per_age <- kar[age %between% c(13, 18), .(vol = uniqueN(date), res = .N), by = .(athlete_id, age)]
v <- dcast(per_age, athlete_id ~ age, value.var = c("vol", "res"), fill = 0)
seasons <- kar[, .(n = .N), by = .(athlete_id, year)][n >= 2]
last_active <- seasons[, .(last = max(year)), by = athlete_id]
r <- merge(koh, last_active, by = "athlete_id", all.x = TRUE)
r[is.na(last), last := base_year]
r <- merge(r, v, by = "athlete_id", all.x = TRUE)
for (c in grep("^(vol|res)_", names(r), value = TRUE)) set(r, which(is.na(r[[c]])), c, 0)
r[, `:=`(alder_ved_slutt = last - birth_year, aktiv_senior = as.integer(last >= birth_year + 20),
         aktiv_17 = as.integer(last >= birth_year + 17), aktiv_naa = as.integer(last >= 2024),
         vol_pre = vol_13 + vol_14, vol_mil = vol_15 + vol_16)]
cat13 <- kar[age %between% c(13, 14), .N, by = .(athlete_id, event_category)]
cat13[, share := N / sum(N), by = athlete_id]
hhi <- cat13[, .(hhi_r = sum(share^2)), by = athlete_id]
r <- merge(r, hhi, by = "athlete_id", all.x = TRUE)

# ---------------------------------------------------------------- row-level comparison
m <- merge(r, ana[, .(athlete_id, a_vol13 = vol_age_13, a_vol14 = vol_age_14, a_vol15 = vol_age_15, a_vol16 = vol_age_16,
                      a_vol17 = vol_age_17, a_vol18 = vol_age_18, a_res14 = res_age_14, a_res16 = res_age_16,
                      a_pre = vol_pre_milepael, a_mil = vol_milepael, a_senior = aktiv_senior, a_17 = aktiv_17,
                      a_naa = aktiv_naa, a_slutt = alder_ved_slutt)],
           by = "athlete_id", all = TRUE)
add("athletes: R-built / analysis file / matched", sprintf("%d / %d / %d", nrow(r), nrow(ana), nrow(m[!is.na(base_year) & !is.na(a_senior)])))
for (p in list(c("vol_13", "a_vol13"), c("vol_14", "a_vol14"), c("vol_15", "a_vol15"), c("vol_16", "a_vol16"),
               c("vol_17", "a_vol17"), c("vol_18", "a_vol18"), c("res_14", "a_res14"), c("res_16", "a_res16"),
               c("vol_pre", "a_pre"), c("vol_mil", "a_mil"), c("aktiv_senior", "a_senior"), c("aktiv_17", "a_17"),
               c("aktiv_naa", "a_naa"), c("alder_ved_slutt", "a_slutt")))
  add(paste0("mismatches: ", p[1]), sum(m[[p[1]]] != m[[p[2]]], na.rm = TRUE) + sum(is.na(m[[p[1]]]) != is.na(m[[p[2]]])))
mh <- merge(r[, .(athlete_id, hhi_r)], r1v, by = "athlete_id")
add("mismatches: HHI 13-14 (> 1e-9 from r1_variables)", sum(abs(mh$hhi_r - mh$hhi_13_14) > 1e-9, na.rm = TRUE))

# ---------------------------------------------------------------- models from the R-built variables
d <- merge(r, r1v[, .(athlete_id, tyr = tyrving_best_r1)], by = "athlete_id")
d[, female := fifelse(gender == "F", 1, fifelse(gender == "M", 0, NA_real_))]
z <- function(x) (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
d[, `:=`(tyr_z = z(tyr), hhi_z = z(hhi_r), vol_z = z(vol_pre))]
wald <- function(f, t) { b <- coef(f)[t]; s <- sqrt(vcov(f)[t, t]); exp(c(b, b - qnorm(.975) * s, b + qnorm(.975) * s)) }
cmp <- function(lab, mine, ref) {
  add(paste0(lab, " (R)"), paste(sprintf("%.4f", mine), collapse = " "))
  add(paste0(lab, " (pipeline)"), paste(sprintf("%.4f", unlist(ref)[seq_along(mine)]), collapse = " "))
  add(paste0(lab, " max abs diff"), sprintf("%.2e", max(abs(mine - unlist(ref)[seq_along(mine)]))))
}
L4 <- aktiv_senior ~ female + tyr_z + hhi_z + vol_z
f4 <- glm(L4, binomial, data = d)
add("Table 3 L4 n", nobs(f4))
for (t in c("female", "tyr_z", "hhi_z", "vol_z")) cmp(paste("Table 3 L4", t, "OR [CI]"), wald(f4, t), RES$primary_L4[[t]][1:3])
for (cc in c("A", "B")) {
  fc <- glm(L4, binomial, data = d[if (cc == "A") birth_year <= 2000 else birth_year >= 2001])
  cmp(paste("Table 7 cohort", cc, "volume OR [CI]"), wald(fc, "vol_z"), RES[[paste0("t7::", cc, "::vol_z")]][1:3])
}
a14 <- d[res_14 >= 1 & !is.na(female) & !is.na(tyr)]
a14[, `:=`(v14_z = z(vol_14), d1415_z = z(vol_15 - vol_14), tyr_zs = z(tyr))]
f2 <- glm(aktiv_senior ~ female + tyr_zs + v14_z + d1415_z, binomial, data = a14)
cmp("Table 4 M2 volume at 14 OR [CI]", wald(f2, "v14_z"), RES$t4$level)
cmp("Table 4 M2 change 14-15 OR [CI]", wald(f2, "d1415_z"), RES$t4$change)
a16 <- d[res_16 >= 2 & !is.na(female)]
a16[, `:=`(v15_z = z(vol_15), d1516_z = z(vol_16 - vol_15))]
f3 <- glm(aktiv_senior ~ female + v15_z + d1516_z, binomial, data = a16)
cmp("Change model at 16, change 15-16 OR [CI]", wald(f3, "d1516_z"), RES$s19$change)
cx <- d[alder_ved_slutt >= 14 & !is.na(female) & !is.na(tyr)]
cx[, `:=`(dur = pmax(alder_ved_slutt - 14, 0.5), ev = as.integer(aktiv_naa == 0))]
fc <- coxph(Surv(dur, ev) ~ female + tyr_z + hhi_z + vol_z, data = cx, ties = "efron")
s <- summary(fc)$conf.int
cmp("Cox, clock from end of age 14, volume HR [CI]", s["vol_z", c(1, 3, 4)], RES$cox14$main$vol_z[1:3])

# ---------------------------------------------------------------- within-athlete fixed-effects event study
grid <- CJ(athlete_id = d$athlete_id, age = 13:19)
pv <- kar[age %between% c(13, 19), .(meets = uniqueN(date)), by = .(athlete_id, age)]
p <- merge(grid, pv, by = c("athlete_id", "age"), all.x = TRUE)[is.na(meets), meets := 0]
p <- merge(p, d[, .(athlete_id, final = alder_ved_slutt, exited = as.integer(aktiv_naa == 0))], by = "athlete_id")
p <- p[exited == 0 | age <= final]
p[, k := fifelse(exited == 1, age - final, -99)]
for (kk in 0:3) set(p, j = paste0("D", kk), value = as.integer(p$k == -kk))
p[, y := log1p(meets)]
p <- p[, if (.N >= 2) .SD, by = athlete_id]
fe <- lm(y ~ D3 + D2 + D1 + D0 + factor(age) + factor(athlete_id), data = p)
vc <- vcovCL(fe, cluster = ~athlete_id, type = "HC0")
for (kk in 3:1) {
  t <- paste0("D", kk); b <- coef(fe)[t]; se <- sqrt(vc[t, t])
  ref <- RES[["es::log(1 + meets), all athletes"]][[t]]
  add(sprintf("Fixed effects T-%d: %% change (R, cluster SE) / pipeline", kk),
      sprintf("%.1f [%.1f, %.1f] / %.1f [%.1f, %.1f]", 100 * (exp(b) - 1), 100 * (exp(b - 1.96 * se) - 1), 100 * (exp(b + 1.96 * se) - 1),
              100 * (exp(ref[1]) - 1), 100 * (exp(ref[2]) - 1), 100 * (exp(ref[3]) - 1)))
}
add("Fixed effects: athletes / athlete-seasons (R)", sprintf("%d / %d", uniqueN(p$athlete_id), nrow(p)))

# ---------------------------------------------------------------- championship types (Supplementary Methods S-M12)
# Written from the rule, with word tokens instead of the pipeline's regular expressions: a type counts
# when the athlete has a result before 17 at a meet whose name identifies it as a district (KM),
# youth-national (UM), junior-national or senior-national (NM) championship. Not championships:
# qualification, preparation, unofficial and test meets, meets abroad, veterans' or school district
# championships, and national championship meets before 15 (side events).
invisible(Sys.setlocale("LC_CTYPE", "en_US.UTF-8"))
cm <- fread(file.path(dir, "corrected", "karrieredata_utvidet.csv"), select = c("athlete_id", "date", "meet_name"), encoding = "UTF-8")
cm[, age := as.integer(substr(date, 1, 4)) - koh$birth_year[match(athlete_id, koh$athlete_id)]]
cm[is.na(meet_name), meet_name := ""]
nm_u <- unique(cm$meet_name)
low <- tolower(nm_u)
tok <- lapply(strsplit(toupper(nm_u), "[^A-Za-z0-9ÆØÅæøå]+"), function(x) x[x != ""])
has_tok <- function(t) vapply(tok, function(x) any(x %in% t), logical(1))
pair <- function(a, b) vapply(tok, function(x) { i <- which(x %in% a); any(i < length(x) & x[pmin(i + 1, length(x))] %in% b) }, logical(1))
starts_tok <- function(pfx) vapply(tok, function(x) any(startsWith(x, pfx)), logical(1))
place <- sub(",.*$", "", nm_u)        # meets abroad: a country code after the town (NIH and TYR are Norwegian venues)
abroad <- grepl("/[A-Z]{3}(/|$)", place) & !grepl("/(NIH|TYR)(/|$)", place)
not_champ <- grepl("kvalifisering|oppkjøring|nm-test", low) | has_tok("UOFF") | abroad
jr <- grepl("juniormesterskap", low) | has_tok(c("JRNM", "JUNIORNM")) | pair(c("JR", "JUNIOR"), "NM") | pair("NM", "JUNIOR")
um <- has_tok("UM") | grepl("u-mester|ungdomsmesterskap", low)
nm_vet <- vapply(tok, function(x) { i <- which(x == "NM"); any(i < length(x) & startsWith(x[pmin(i + 1, length(x))], "VETERAN")) }, logical(1))
nm <- (has_tok("NM") | grepl("norgesmesterskap", low)) & !nm_vet & !jr & !um
vet_school <- (grepl("veteran|vetraner|videregående", low) | has_tok("VET")) &
  !(grepl("[0-9]+ ?- ?[0-9]+ ?år|senior", low) | nm_vet)
km <- (starts_tok("KM") | grepl("kretsme(i)?ster|distriktsme(i)?ster", low)) & !vet_school
type <- data.table(meet_name = nm_u, not_champ, jr, um, nm, km)
cm <- merge(cm, type, by = "meet_name")
cm[, national := age >= 15 & !not_champ]
pre <- cm[age < 17, .(t_um = any(um & national), t_jr = any(jr & national), t_nm = any(nm & national),
                      t_km = any(km & !not_champ)), by = athlete_id]
pre[, n_types := t_um + t_jr + t_nm + t_km]
u1516 <- cm[age %between% c(15, 16), .(um1516 = as.integer(any(um & national))), by = athlete_id]
ct <- merge(ana[, .(athlete_id, a_types = n_msk_typer, a_um = um_15_16)], pre[, .(athlete_id, n_types)], by = "athlete_id", all.x = TRUE)
ct <- merge(ct, u1516, by = "athlete_id", all.x = TRUE)
ct[is.na(n_types), n_types := 0][is.na(um1516), um1516 := 0]
add("mismatches: championship types before 17", sum(ct$n_types != ct$a_types))
add("mismatches: youth championship at 15-16", sum(ct$um1516 != ct$a_um))
l16 <- merge(d[alder_ved_slutt >= 16], ct[, .(athlete_id, n_types)], by = "athlete_id")
l16[, vol1516_z := (vol_mil - mean(d$vol_mil)) / sd(d$vol_mil)]
l16 <- l16[!is.na(female) & !is.na(tyr_z)]
l16[, `:=`(dur = pmax(alder_ved_slutt - 16, 0.5), ev = as.integer(aktiv_naa == 0))]
fl <- coxph(Surv(dur, ev) ~ female + tyr_z + hhi_z + vol1516_z + n_types, data = l16, ties = "efron")
sl <- summary(fl)$conf.int
cmp("Landmark Cox at 16, volume 15-16 HR [CI]", sl["vol1516_z", c(1, 3, 4)], RES$lm16$vol1516_z[1:3])
cmp("Landmark Cox at 16, championship types HR [CI]", sl["n_types", c(1, 3, 4)], RES$lm16$n_msk_typer[1:3])

o <- rbindlist(out)
fwrite(o, file.path(here, "audit_06_summary.csv"))
print(o, nrows = 200)
