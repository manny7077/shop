// src/stores/permission.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePermissionStore = defineStore('permission', () => {
  const role = ref(localStorage.getItem('role') || null)
  
  const isManager = computed(() => role.value === 'Manager')
  const isStockClerk = computed(() => role.value === 'Stock Clerk')
  const isSalesPerson = computed(() => role.value === 'Sales Person')
  
  function setRole(newRole) {
    role.value = newRole
    localStorage.setItem('role', newRole)
  }
  
  return { role, isManager, isStockClerk, isSalesPerson, setRole }
})