import { useQuery } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import { Bell } from "lucide-react"

import { NotificationsService } from "@/client"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function NotificationBell() {
  const { data } = useQuery({
    queryKey: ["notifications-unread-count"],
    queryFn: () => NotificationsService.getUnreadCount(),
    refetchInterval: 30000,
  })

  const unreadCount = data?.unread_count ?? 0

  return (
    <Button variant="ghost" size="sm" className="relative size-9 p-0" asChild>
      <Link to="/notifications">
        <Bell className="size-5" />
        {unreadCount > 0 && (
          <span
            className={cn(
              "absolute -top-1 -right-1 flex items-center justify-center",
              "min-w-[18px] h-[18px] px-1 rounded-full",
              "bg-destructive text-destructive-foreground",
              "text-xs font-medium",
            )}
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
        <span className="sr-only">
          Notifications {unreadCount > 0 && `(${unreadCount} unread)`}
        </span>
      </Link>
    </Button>
  )
}

export default NotificationBell
