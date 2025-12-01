import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import workflowsRouter from './routes/workflows.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes - Önce route'ları import et ve kullan
try {
  app.use('/api/workflows', workflowsRouter);
  console.log('✅ Route\'lar yüklendi: /api/workflows');
} catch (error) {
  console.error('❌ Route yükleme hatası:', error);
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'API çalışıyor' });
});

// 404 handler - API route'ları için
app.use('/api/*', (req, res) => {
  res.status(404).json({ error: 'API endpoint bulunamadı', path: req.path });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({ 
    message: 'İş Akışı Yönetimi API',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      workflows: '/api/workflows'
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('❌ Server Error:', err.stack);
  res.status(500).json({ 
    error: 'Bir hata oluştu',
    message: err.message 
  });
});

// Server'ı başlat
const server = app.listen(PORT, () => {
  console.log(`🚀 Server ${PORT} portunda çalışıyor`);
  console.log(`📡 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📡 API: http://localhost:${PORT}/api`);
  console.log(`🏥 Health Check: http://localhost:${PORT}/api/health`);
  console.log(`📋 Workflows: http://localhost:${PORT}/api/workflows`);
});

export default server;

