import type { ColumnDef } from "@tanstack/react-table"
import type { NotificationPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { NotificationActionsMenu } from "./NotificationActionsMenu"

export const columns: ColumnDef<NotificationPublic>[] = [
  {
    accessorKey: "message",
    header: "Message",
    cell: ({ row }) => {
      const message = row.original.message
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "font-medium",
              !row.original.is_read && "font-semibold",
            )}
          >
            {message}
          </span>
          {!row.original.is_read && (
            <span className="size-2 rounded-full bg-blue-500" />
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) => {
      const type = row.original.type
      const variants: Record<string, "default" | "secondary"> = {
        mention: "default",
        like: "secondary",
      }
      return <Badge variant={variants[type] || "default"}>{type}</Badge>
    },
  },
  {
    accessorKey: "is_read",
    header: "Status",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_read ? "bg-gray-400" : "bg-blue-500",
          )}
        />
        <span className={row.original.is_read ? "text-muted-foreground" : ""}>
          {row.original.is_read ? "Read" : "Unread"}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "created_at",
    header: "Date",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {row.original.created_at
          ? new Date(row.original.created_at).toLocaleDateString()
          : "-"}
      </span>
    ),
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <NotificationActionsMenu notification={row.original} />
      </div>
    ),
  },
]
