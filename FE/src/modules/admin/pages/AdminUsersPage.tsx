import { usePermission } from '@/core/auth/use-permission'
import { useTranslation } from 'react-i18next'
import { AdminHeader } from '../components/AdminHeader'
import { useAdminRoles, useAdminUsers, useUpdateUserRoles } from '../hooks/use-admin-data'
import { useAdminLabel } from '../hooks/use-admin-label'

export function AdminUsersPage() {
  const { t } = useTranslation('admin')
  const label = useAdminLabel()
  const canManage = usePermission('users.manage_roles')
  const users = useAdminUsers()
  const roles = useAdminRoles()
  const updateRoles = useUpdateUserRoles()

  return (
    <>
      <AdminHeader eyebrow={t('users.eyebrow')} title={t('users.title')} />
      <section className="admin-panel">
        <div className="admin-table admin-table--users">
          <div className="admin-table__head">
            <span>{t('table.user')}</span>
            <span>{t('table.email')}</span>
            <span>{t('table.currentRole')}</span>
            <span>{t('table.access')}</span>
          </div>
          {users.data?.map((user) => {
            let currentRole = ''
            if (user.roles.length > 0) {
              currentRole = user.roles[0]
            }
            let accessControl = <span>{t('users.readOnly')}</span>
            if (canManage) {
              accessControl = (
                <select
                  value={currentRole}
                  disabled={updateRoles.isPending}
                  onChange={(event) =>
                    updateRoles.mutate({ id: user.id, roles: [event.target.value] })
                  }
                >
                  {roles.data?.map((role) => (
                    <option key={role.id} value={role.name}>
                      {label('role', role.name, role.label)}
                    </option>
                  ))}
                </select>
              )
            }

            return (
              <div className="admin-table__row" key={user.id}>
                <strong>{user.name}</strong>
                <span>{user.email}</span>
                <span>{user.roles.map((role) => label('role', role)).join(', ')}</span>
                {accessControl}
              </div>
            )
          })}
        </div>
      </section>
    </>
  )
}
