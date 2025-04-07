import { createRouter, createWebHashHistory, createWebHistory } from "vue-router";
import { LocalStorage } from "quasar";
import routes from "./routes"; // Import routes

export default function defineRouter() {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    history: createHistory(process.env.VUE_ROUTER_BASE),
    routes,
    scrollBehavior: () => ({ left: 0, top: 0 }),
  });

  // 🔐 Global Navigation Guard (Authentication Check)
  Router.beforeEach((to, from, next) => {
    const token = LocalStorage.getItem("token");

    if (to.meta.requiresAuth && !token) {
      next("/login"); // Redirect to login if not authenticated
    } else {
      next(); // Continue to route
    }
  });

  return Router;
}
