-- Migration: Add weight-specific events for throwing implements
-- This creates separate events for different weight classes in shot put, discus, hammer, and javelin

-- Shot put (Kule) - various weights
INSERT INTO events (code, name, result_type, event_category, sort_order) VALUES
  ('kule_2kg', 'Kule 2,0kg', 'distance', 'throw', 201),
  ('kule_3kg', 'Kule 3,0kg', 'distance', 'throw', 202),
  ('kule_4kg', 'Kule 4,0kg', 'distance', 'throw', 203),
  ('kule_5kg', 'Kule 5,0kg', 'distance', 'throw', 204),
  ('kule_6kg', 'Kule 6,0kg', 'distance', 'throw', 205),
  ('kule_7_26kg', 'Kule 7,26kg', 'distance', 'throw', 206)
ON CONFLICT (code) DO NOTHING;

-- Discus - various weights
INSERT INTO events (code, name, result_type, event_category, sort_order) VALUES
  ('diskos_600g', 'Diskos 600gram', 'distance', 'throw', 211),
  ('diskos_750g', 'Diskos 750gram', 'distance', 'throw', 212),
  ('diskos_1kg', 'Diskos 1,0kg', 'distance', 'throw', 213),
  ('diskos_1_5kg', 'Diskos 1,5kg', 'distance', 'throw', 214),
  ('diskos_1_75kg', 'Diskos 1,75kg', 'distance', 'throw', 215),
  ('diskos_2kg', 'Diskos 2,0kg', 'distance', 'throw', 216)
ON CONFLICT (code) DO NOTHING;

-- Hammer (Slegge) - various weights
INSERT INTO events (code, name, result_type, event_category, sort_order) VALUES
  ('slegge_2kg', 'Slegge 2,0kg', 'distance', 'throw', 221),
  ('slegge_3kg', 'Slegge 3,0kg', 'distance', 'throw', 222),
  ('slegge_4kg', 'Slegge 4,0kg', 'distance', 'throw', 223),
  ('slegge_5kg', 'Slegge 5,0kg', 'distance', 'throw', 224),
  ('slegge_6kg', 'Slegge 6,0kg', 'distance', 'throw', 225),
  ('slegge_7_26kg', 'Slegge 7,26kg', 'distance', 'throw', 226)
ON CONFLICT (code) DO NOTHING;

-- Javelin (Spyd) - various weights
INSERT INTO events (code, name, result_type, event_category, sort_order) VALUES
  ('spyd_400g', 'Spyd 400gram', 'distance', 'throw', 231),
  ('spyd_500g', 'Spyd 500gram', 'distance', 'throw', 232),
  ('spyd_600g', 'Spyd 600gram', 'distance', 'throw', 233),
  ('spyd_700g', 'Spyd 700gram', 'distance', 'throw', 234),
  ('spyd_800g', 'Spyd 800gram', 'distance', 'throw', 235)
ON CONFLICT (code) DO NOTHING;

-- Keep the generic events (kule, diskos, slegge, spyd) for backward compatibility
-- They will be used when the weight is not specified
