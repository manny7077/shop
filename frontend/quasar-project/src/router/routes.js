const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/ProductsPage.vue'), meta: { requiresAuth: true } },
      { path: 'sales/', component: () => import('pages/SalesPage.vue') },
      { path: 'login/', component: () => import('pages/Login.vue') },
      { path: 'audit/', component: () => import('pages/AuditLogs.vue') },
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
