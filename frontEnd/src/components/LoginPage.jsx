import { useState } from 'react'
import './LoginPage.css'

const LoginPage = () => {
  const [userType, setUserType] = useState(null) // null, 'admin', or 'user'
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const handleUserTypeSelect = (type) => {
    setUserType(type)
    setFormData({ email: '', password: '' })
  }

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Şimdilik sadece tasarım, fonksiyonellik eklenmeyecek
    console.log('Login attempt:', userType, formData)
  }

  const handleBack = () => {
    setUserType(null)
    setFormData({ email: '', password: '' })
  }

  return (
    <div className="login-container">
      {!userType ? (
        <div className="welcome-screen">
          <div className="welcome-header">
            <div className="logo">
              <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" fill="#FFD700" stroke="#FFA500" strokeWidth="2"/>
                <text x="50" y="65" fontSize="50" fontWeight="bold" fill="#0a0e27" textAnchor="middle">İ</text>
              </svg>
            </div>
            <h1 className="welcome-title">İş Akış Yönetim Sistemi</h1>
            <p className="welcome-subtitle">Sisteme giriş yapmak için bir seçenek seçin</p>
          </div>
          
          <div className="login-cards-container">
            <div
              className="login-card-item user-card"
              onClick={() => handleUserTypeSelect('user')}
            >
              <div className="card-icon-wrapper user-icon-wrapper">
                <svg className="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h2 className="card-title">Kullanıcı Girişi</h2>
              <p className="card-description">Normal kullanıcılar için giriş sayfası. Dashboard ve sistem sayfalarına erişim sağlar.</p>
              <div className="card-action">
                <span className="action-text">Giriş Yap</span>
                <svg className="arrow-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>

            <div
              className="login-card-item admin-card"
              onClick={() => handleUserTypeSelect('admin')}
            >
              <div className="card-icon-wrapper admin-icon-wrapper">
                <svg className="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L4 5V11C4 16.55 7.16 21.74 12 23C16.84 21.74 20 16.55 20 11V5L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h2 className="card-title">Admin Girişi</h2>
              <p className="card-description">Yöneticiler için özel giriş sayfası. Admin paneli ve sistem yönetimi erişimi sağlar.</p>
              <div className="card-action">
                <span className="action-text">Giriş Yap</span>
                <svg className="arrow-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
          </div>

          <div className="footer">
            <p>© 2025 İş Akış Yönetim Sistemi. Tüm hakları saklıdır.</p>
          </div>
        </div>
      ) : (
        <div className="login-card">
          <div className="login-form-container">
            <button className="back-button" onClick={handleBack}>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            
            <div className="login-header">
              <div className={`user-type-icon ${userType}`}>
                {userType === 'admin' ? (
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M20.59 22C20.59 18.13 16.74 15 12 15C7.26 15 3.41 18.13 3.41 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M20 8L22 10L20 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M4 8L2 10L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </div>
              <h1 className="login-title">
                {userType === 'admin' ? 'Admin Girişi' : 'Kullanıcı Girişi'}
              </h1>
              <p className="login-subtitle">Hesabınıza giriş yapın</p>
            </div>

            <form className="login-form" onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email">E-posta</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="ornek@email.com"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Şifre</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="••••••••"
                  required
                />
              </div>

              <div className="form-options">
                <label className="remember-me">
                  <input type="checkbox" />
                  <span>Beni hatırla</span>
                </label>
                <a href="#" className="forgot-password">Şifremi unuttum</a>
              </div>

              <button type="submit" className="login-button">
                Giriş Yap
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default LoginPage

