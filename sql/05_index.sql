CREATE INDEX idx_appointment_slot ON appointment(dock_id,status,starts_at,ends_at);
CREATE INDEX idx_visit_status ON truck_visit(status,vehicle_id);
CREATE INDEX idx_event_period ON visit_event(state,happened_at,visit_id);
CREATE INDEX idx_movement_stock ON stock_movement(receipt_item_id,location_id,id);
CREATE INDEX idx_movement_period ON stock_movement(created_at,kind);
CREATE INDEX idx_lot_fefo ON lot(article_id,blocked,expires_on,id);
CREATE INDEX idx_pick_reservation ON pick(receipt_item_id,location_id,status);
CREATE INDEX idx_notice_date ON supplier_notice(expected_on,supplier_id);
