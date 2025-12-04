import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import WorkflowList from './pages/WorkflowList'
import WorkflowEditor from './pages/WorkflowEditor'
import IssueList from './pages/IssueList'
import IssueEditor from './pages/IssueEditor'
import IssueBoard from './pages/IssueBoard'
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
          <Route path="/issues" element={<IssueList />} />
          <Route path="/issues/board" element={<IssueBoard />} />
          <Route path="/issues/new" element={<IssueEditor />} />
          <Route path="/issues/:id" element={<IssueEditor />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

