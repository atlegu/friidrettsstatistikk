# delong_bro.R — A1-audit: (1) DeLong-differansene i r1_delong.csv kontrollert med pROC
# på de samme out-of-fold-prediksjonene; (2) kalibrering fra OOF; (3) uavhengig 5x20
# stratifisert CV i R (andre splitter enn sklearn — sammenlignes omtrentlig).

suppressMessages({library(data.table); library(pROC)})
setwd(dirname(dirname(normalizePath(sub("--file=", "", grep("--file=", commandArgs(FALSE), value = TRUE)[1])))))

o <- fread("audit/oof.csv")
res <- rbindlist(lapply(list(c("M2_minus_M1", "m2", "m1"),
                             c("volum+fremgang_minus_volum+niva", "frem", "niva")), function(k) {
  ra <- roc(o$y, o[[k[2]]], direction = "<", quiet = TRUE)
  rb <- roc(o$y, o[[k[3]]], direction = "<", quiet = TRUE)
  t <- roc.test(ra, rb, paired = TRUE, method = "delong")
  d <- as.numeric(auc(ra) - auc(rb))
  se <- d / t$statistic
  data.table(kontrast = k[1], auc_a = as.numeric(auc(ra)), auc_b = as.numeric(auc(rb)),
             diff = d, ki_lav = d - qnorm(.975) * abs(se), ki_hoy = d + qnorm(.975) * abs(se),
             p = t$p.value)
}))
fwrite(res, "audit/r_out/delong_proc.csv")

lp <- qlogis(pmin(pmax(o$m2, 1e-6), 1 - 1e-6))
kal <- glm(o$y ~ lp, family = binomial)
fwrite(data.table(kalibreringsslope = coef(kal)[2], brier = mean((o$y - o$m2)^2)),
       "audit/r_out/kalibrering.csv")

# Uavhengig CV: modellmatrise bygges i R fra analysedata (region utelatt — konstant)
ad <- fread("data_private/analysedata.csv")
d <- ad[kohort_primar == TRUE & skaarbar == TRUE & liten_gruppecelle == FALSE]
d[, lk := fifelse(is.na(log_klubbstorrelse), median(d$log_klubbstorrelse, na.rm = TRUE),
                  log_klubbstorrelse)]
for (v in c("vol1314", "vol1516")) d[, paste0(v, "_g") := (get(v) - mean(get(v))) / sd(get(v))]
d <- d[!is.na(delta_z) & !is.na(niva_w1_z)]
d[, bk := factor(birth_year)]
f <- list(
  m1 = senior ~ gender + bk + lk + niva_w1_z + vol1314_g + vol1516_g + k13 + k15,
  m2 = senior ~ gender + bk + lk + niva_w1_z + vol1314_g + vol1516_g + k13 + k15 + delta_z,
  frem = senior ~ gender + vol1314_g + vol1516_g + k13 + k15 + delta_z,
  niva = senior ~ gender + vol1314_g + vol1516_g + k13 + k15 + niva_w1_z)
set.seed(20261030)
cvauc <- sapply(f, function(ff) mean(sapply(1:20, function(r) {
  fold <- integer(nrow(d))
  for (cl in 0:1) { i <- which(d$senior == cl); fold[i] <- sample(rep(1:5, length.out = length(i))) }
  mean(sapply(1:5, function(k) {
    m <- glm(ff, binomial, d[fold != k])
    p <- predict(m, d[fold == k], type = "response")
    as.numeric(auc(roc(d$senior[fold == k], p, direction = "<", quiet = TRUE)))
  }))
})))
fwrite(as.data.table(as.list(cvauc)), "audit/r_out/cv_auc_uavhengig.csv")
cat("delong_bro ferdig\n")
