import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Check, MoreHorizontal, Trash2 } from "lucide-react"

import { type NotificationPublic, NotificationsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface NotificationActionsMenuProps {
  notification: NotificationPublic
}

export function NotificationActionsMenu({
  notification,
}: NotificationActionsMenuProps) {
  const queryClient = useQueryClient()

  const markAsReadMutation = useMutation({
    mutationFn: () => NotificationsService.markAsRead({ id: notification.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      queryClient.invalidateQueries({
        queryKey: ["notifications-unread-count"],
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () =>
      NotificationsService.deleteNotification({ id: notification.id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] })
      queryClient.invalidateQueries({
        queryKey: ["notifications-unread-count"],
      })
    },
  })

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="size-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {!notification.is_read && (
          <DropdownMenuItem
            onClick={() => markAsReadMutation.mutate()}
            disabled={markAsReadMutation.isPending}
          >
            <Check className="mr-2 size-4" />
            Mark as read
          </DropdownMenuItem>
        )}
        <DropdownMenuItem
          onClick={() => deleteMutation.mutate()}
          disabled={deleteMutation.isPending}
          className="text-destructive"
        >
          <Trash2 className="mr-2 size-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
