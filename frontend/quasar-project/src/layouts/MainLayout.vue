<template>
  <q-layout view="hHh lpR lFf">
    <!-- HEADER - Only show when authenticated -->
    <q-header v-if="isAuthenticated" elevated class="bg-primary text-white">
      <q-toolbar>
        <!-- SHOP NAME -->
        <q-toolbar-title>
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo-v2/svg/logo-mono-white.svg">
          </q-avatar>
          {{ shopName }}
        </q-toolbar-title>

        <!-- USER MENU -->
        <q-btn-dropdown
          flat
          color="white"
          icon="account_circle"
          :label="fullName"
          auto-close
          class="q-ml-auto"
        >
          <q-list>
            <q-item clickable v-close-popup @click="logout">
              <q-item-section avatar>
                <q-icon name="logout" />
              </q-item-section>
              <q-item-section>Logout</q-item-section>
              <q-item-section side>
                <q-spinner v-if="logoutLoading" size="sm" />
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <!-- MAIN CONTENT -->
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { api } from 'src/boot/axios';

const $q = useQuasar();
const router = useRouter();
const logoutLoading = ref(false);

// Create a reactive reference that we can update
const authState = ref(!!localStorage.getItem('token'));

// Watch for storage events (for cross-tab synchronization)
window.addEventListener('storage', () => {
  authState.value = !!localStorage.getItem('token');
});

// Reactive authentication state
const isAuthenticated = computed(() => authState.value);

// Use computed properties for reactive data
const shopName = computed(() => localStorage.getItem('shop_name') || 'Shop');
const fullName = computed(() => {
  const firstName = localStorage.getItem('first_name') || '';
  const lastName = localStorage.getItem('last_name') || '';
  return `${firstName} ${lastName}`.trim() || 'User';
});

const logout = async () => {
  logoutLoading.value = true;
  
  try {
    const token = localStorage.getItem('token');
    if (token) {
      await api.post('/logout/');
    }
    
    $q.notify({
      type: 'positive',
      message: 'Logged out successfully'
    });
  } catch (error) {
    $q.notify({
      type: 'warning',
      message: 'Logged out locally (backend logout failed)'
    });
    console.error('Logout error:', error);
  } finally {
    // Clear all auth data
    localStorage.removeItem('token');
    localStorage.removeItem('shop_name');
    localStorage.removeItem('first_name');
    localStorage.removeItem('last_name');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    sessionStorage.clear();
    
    // Update auth state to trigger re-render
    authState.value = false;
    
    // Redirect to login
    router.push('/login');
    logoutLoading.value = false;
  }
};

// Force update when route changes (helps with login redirect)
watchEffect(() => {
  router.currentRoute.value;
  authState.value = !!localStorage.getItem('token');
});
</script>