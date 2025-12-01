import { Pool } from 'pg';

// Default PostgreSQL configuration for application database
const DEFAULT_APP_CONFIG = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'is_akis',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
  // Connection pool ayarları
  max: 20, // Maximum number of clients in the pool
  min: 2, // Minimum number of clients in the pool
  idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
  connectionTimeoutMillis: 2000, // Return an error after 2 seconds if connection cannot be established
  allowExitOnIdle: false, // Don't exit process when pool is idle
};

// Create a singleton pool for application database
const appPool = new Pool(DEFAULT_APP_CONFIG);

// Error handler - sadece logla, process'i kapatma
appPool.on('error', (err, client) => {
  console.error('Unexpected error on idle database client', err);
  // Process'i kapatmak yerine sadece logla
  // Eğer client varsa, bağlantıyı kapat
  if (client) {
    client.release();
  }
});

// Pool bağlantı durumu loglama
appPool.on('connect', () => {
  console.log('✅ Database connection established');
});

appPool.on('remove', () => {
  console.log('🔌 Database connection removed');
});

export default appPool;
