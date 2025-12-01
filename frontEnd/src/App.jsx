import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import WorkflowList from './pages/WorkflowList'
import WorkflowEditor from './pages/WorkflowEditor'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workflows" element={<WorkflowList />} />
          <Route path="/workflows/:id" element={<WorkflowEditor />} />
          <Route path="/workflows/new" element={<WorkflowEditor />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

