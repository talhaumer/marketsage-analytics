import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Analyst } from './pages/Analyst'
import { History } from './pages/History'
import { Portfolio } from './pages/Portfolio'

const router = createBrowserRouter([
  { path: '/', element: <Layout><Analyst /></Layout> },
  { path: '/history', element: <Layout><History /></Layout> },
  { path: '/portfolio', element: <Layout><Portfolio /></Layout> },
])

export default function App() {
  return <RouterProvider router={router} />
}
