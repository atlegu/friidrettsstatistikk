library(data.table)
library(fixest)

root <- "/Users/atleguttormsen/Dropbox/Aktuelt1/Florida25/shoes"
out  <- "/private/tmp/claude-501/-Users-atleguttormsen-Dropbox-Aktuelt1-Florida25-shoes/29f1a5c6-2414-4592-95db-61b63dba3969/scratchpad"

SAMPLE_START <- 2015L
panel <- readRDS(file.path(root, "data", "processed", "ncaa_analysis_ready.rds"))
panel <- panel[academic_year >= SAMPLE_START & academic_year != 2020L]

ref_stats <- panel[academic_year %in% 2015:2018,
                   .(ref_mean = mean(mark_numeric, na.rm = TRUE),
                     ref_sd   = sd(mark_numeric, na.rm = TRUE)),
                   by = .(event, gender)]
panel <- merge(panel, ref_stats, by = c("event", "gender"))
panel[, z_fixed := fifelse(is_timed,
                           -(mark_numeric - ref_mean) / ref_sd,
                            (mark_numeric - ref_mean) / ref_sd)]

dist_map <- data.table(
  event = c("60","100","200","400","60H","100H","110H","400H",
            "800","1500","MILE","3000","3000S","5000","10000"),
  race_distance = c(60,100,200,400,60,100,110,400,
                    800,1500,1609,3000,3000,5000,10000))
panel <- merge(panel, dist_map, by = "event", all.x = TRUE)

panel[, rank_in_year := frank(fifelse(is_timed, mark_numeric, -mark_numeric)),
      by = .(event, gender, academic_year)]
topN <- panel[rank_in_year <= 100L]

## ---- Figur 1: trend (top-100) ----
trend <- topN[, .(mean_z = mean(z_fixed, na.rm = TRUE), n = .N),
              by = .(academic_year, treatment_group)]
fwrite(trend[order(treatment_group, academic_year)], file.path(out, "fagnytt_trend.csv"))

## ---- Figur 2: dose-response ----
running_events <- unique(topN[treatment_group != "control", event])
field_data <- topN[treatment_group == "control"]
res <- list()
for (ev in running_events) {
  ev_data <- topN[event == ev]
  ev_tg <- ev_data$treatment_group[1]
  ty <- if (ev_tg == "distance_spikes") 2021L else 2022L
  combined <- rbind(ev_data, field_data, fill = TRUE)
  combined[, did_ev := as.integer(event == ev & academic_year >= ty)]
  m <- feols(z_fixed ~ did_ev | event^gender, data = combined, cluster = ~event^gender)
  res[[ev]] <- data.table(event = ev, treatment_group = ev_tg,
                          race_distance = unique(ev_data$race_distance),
                          coef = coef(m)["did_ev"], se = se(m)["did_ev"],
                          pval = pvalue(m)["did_ev"])
}
dose <- rbindlist(res)
dose[, `:=`(log_dist = log(race_distance),
            ci_lo = coef - 1.96 * se, ci_hi = coef + 1.96 * se)]
fwrite(dose[order(race_distance)], file.path(out, "fagnytt_dose.csv"))

dose_lm <- lm(coef ~ log_dist, data = dose, weights = 1/se^2)
cat(sprintf("WLS slope = %.4f (SE %.4f, p = %.4g)\n",
            coef(dose_lm)["log_dist"],
            summary(dose_lm)$coefficients["log_dist","Std. Error"],
            summary(dose_lm)$coefficients["log_dist","Pr(>|t|)"]))
cat("Ferdig.\n")
