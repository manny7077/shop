<template>
    <q-dialog v-model="modelValue">
      <q-card style="width: 400px">
        <q-card-section>
          <div class="text-h6">Add New Product</div>
        </q-card-section>
  
        <q-card-section>
          <q-input v-model="form.name" label="Product Name" outlined dense />
          <q-input v-model="form.category" label="Category" outlined dense />
          <q-input v-model.number="form.price" label="Price" type="number" outlined dense />
          <q-input v-model.number="form.quantity" label="Quantity" type="number" outlined dense />
        </q-card-section>
  
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="negative" v-close-popup />
          <q-btn label="Add" color="primary" @click="addProduct" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </template>
  
  <script setup>
  import { ref, defineEmits, defineProps } from 'vue';
  import { useQuasar } from 'quasar';
  import { api } from 'src/boot/axios';
  
  const $q = useQuasar();
  const emit = defineEmits(['refresh']);
  const modelValue = defineProps(['modelValue']);
  
  const form = ref({
    name: '',
    category: '',
    price: 0,
    quantity: 1
  });
  
  const addProduct = async () => {
    try {
      await api.post('products/', form.value);
      $q.notify({ message: 'Product added', color: 'positive', icon: 'check' });
      emit('refresh');
    } catch (error) {
      $q.notify({ message: 'Error adding product', color: 'negative', icon: 'error' });
    }
  };
  </script>
  