import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Bell } from "lucide-react"
import { Suspense } from "react"

import { NotificationsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { columns } from "@/components/Notifications/columns"
import PendingNotifications from "@/components/Pending/PendingNotifications"

function getNotificationsQueryOptions() {
  return {
    queryFn: () =>
      NotificationsService.readNotifications({ skip: 0, limit: 100 }),
    queryKey: ["notifications"],
  }
}

export const Route = createFileRoute("/_layout/notifications")({
  component: Notifications,
  head: () => ({
    meta: [
      {
        title: "Notifications - FastAPI Cloud",
      },
    ],
  }),
})

function NotificationsTableContent() {
  const { data: notifications } = useSuspenseQuery(
    getNotificationsQueryOptions(),
  )

  if (notifications.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 rounded-full bg-muted p-4">
          <Bell className="size-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No notifications yet</h3>
        <p className="text-muted-foreground">
          You'll see notifications here when you receive them
        </p>
      </div>
    )
  }

  return <DataTable columns={columns} data={notifications.data} />
}

function NotificationsTable() {
  return (
    <Suspense fallback={<PendingNotifications />}>
      <NotificationsTableContent />
    </Suspense>
  )
}

function Notifications() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">
            View and manage your notifications
          </p>
        </div>
      </div>
      <NotificationsTable />
    </div>
  )
}
