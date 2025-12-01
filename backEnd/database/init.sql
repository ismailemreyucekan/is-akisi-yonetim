-- İş Akışları tablosu
CREATE TABLE IF NOT EXISTS is_akisi (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    aciklama TEXT,
    adimlar JSONB NOT NULL DEFAULT '[]'::jsonb,
    baglantilar JSONB NOT NULL DEFAULT '[]'::jsonb,
    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Güncelleme tarihi için trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.guncelleme_tarihi = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_is_akisi_updated_at 
    BEFORE UPDATE ON is_akisi
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_is_akisi_ad ON is_akisi(ad);
CREATE INDEX IF NOT EXISTS idx_is_akisi_olusturma_tarihi ON is_akisi(olusturma_tarihi);

