import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // localStorage'dan tema tercihini al
    const savedTheme = localStorage.getItem('theme')
    const initialTheme = savedTheme || 'light'
    // İlk render'da hemen uygula
    document.documentElement.setAttribute('data-theme', initialTheme)
    return initialTheme
  })

  useEffect(() => {
    // Tema değiştiğinde localStorage'a kaydet ve body'ye class ekle
    localStorage.setItem('theme', theme)
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'))
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

