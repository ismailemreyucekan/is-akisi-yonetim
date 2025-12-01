import pool from './database.js'

// Bağlantıyı test et
async function testConnection() {
  try {
    const result = await pool.query('SELECT NOW()')
    console.log('✅ Veritabanı bağlantısı başarılı!')
    console.log('Sunucu zamanı:', result.rows[0].now)
    await pool.end()
    process.exit(0)
  } catch (error) {
    console.error('❌ Veritabanı bağlantı hatası:', error.message)
    console.error('\nLütfen kontrol edin:')
    console.error('1. PostgreSQL servisinin çalıştığından emin olun')
    console.error('2. .env dosyasının backEnd klasöründe olduğundan emin olun')
    console.error('3. .env dosyasındaki DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD değerlerini kontrol edin')
    console.error('4. Veritabanının oluşturulduğundan emin olun: CREATE DATABASE workflow_db;')
    process.exit(1)
  }
}

testConnection()

