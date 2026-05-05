import { Sidebar } from './Sidebar'

export function Layout({ children }) {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <Sidebar />
      <main className="flex-1 ml-52 overflow-auto flex flex-col">{children}</main>
    </div>
  )
}
