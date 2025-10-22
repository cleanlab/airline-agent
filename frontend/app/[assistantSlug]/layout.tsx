type LayoutProps = {
  children: React.ReactNode
}

export default async function ChatLayout({ children }: LayoutProps) {
  return <div className="relative flex h-dvh overflow-hidden">{children}</div>
}
