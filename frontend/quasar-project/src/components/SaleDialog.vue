<script setup>
import { ref, computed, onMounted } from "vue";
import { useQuasar } from "quasar";
import { api } from "src/boot/axios";
import { Notify } from "quasar";
// Define props & emits
const props = defineProps({ modelValue: Boolean });
const emit = defineEmits(["saleRecorded", "update:modelValue"]);

const $q = useQuasar();

const saleItems = ref([{ product: null, quantity: 1 }]); // Default entry
const products = ref([]); // Store fetched products

// Fetch products from API
const fetchProducts = async () => {
  try {
    const response = await api.get("products/");
    products.value = response.data;
  } catch (error) {
    console.error("Error fetching products:", error);
  }
};

// Run on component mount
onMounted(fetchProducts);

// Add another product row
const addProductRow = () => {
  saleItems.value.push({ product: null, quantity: 1 });
};

// Remove product row
const removeProductRow = (index) => {
  saleItems.value.splice(index, 1);
};

// Compute total price
const totalPrice = computed(() => {
  return saleItems.value.reduce((sum, item) => {
    const price = item.product?.price ? parseFloat(item.product.price) : 0;
    return sum + (item.quantity * price);
  }, 0).toFixed(2);
});

// Submit sale
const recordSale = async () => {
  if (saleItems.value.some(item => !item.product)) {
    $q.notify({ type: "warning", message: "Please select a product for each row." });
    return;
  }

  // Check for stock availability before sending the request
  const outOfStockItems = saleItems.value.filter(item => item.quantity > item.product.quantity);
  if (outOfStockItems.length > 0) {
    const productNames = outOfStockItems.map(item => item.product.name).join(", ");
    $q.notify({ 
      type: "warning", 
      message: `Insufficient stock for: ${productNames}. Adjust quantity.`,
    });
    return;
  }

  try {
    const saleData = saleItems.value.map(item => ({
      product_id: item.product.id,
      quantity: Number(item.quantity),
    }));

    await api.post("sales/record/", { sales: saleData });

    $q.notify({ message: "Product sold successfully!", color: "positive", icon: "check" });

    emit("saleRecorded");
    emit("update:modelValue", false); // Close dialog
  } catch (error) {
    if (error.response?.data?.error) {
      $q.notify({ message: error.response.data.error, color: "negative" });
    } else {
      $q.notify({ message: "Error recording sale.", color: "negative" });
    }
    console.error("Error recording sale:", error);
  }
};
const filteredProducts = ref([...products.value]);

const filterProducts = (val, update) => {
  if (val === '') {
    update(() => { filteredProducts.value = products.value; });
    return;
  }
  const needle = val.toLowerCase();
  update(() => {
    filteredProducts.value = products.value.filter(p => p.name.toLowerCase().includes(needle));
  });
};

</script>

<template>
  <q-dialog v-model="props.modelValue">
    <q-card class="q-pa-lg q-dialog-card">
      <!-- Title -->
      <q-card-section class="text-center">
        <div class="text-h5 text-primary">Record Sale</div>
      </q-card-section>

      <!-- Sale Items Section -->
      <q-card-section class="q-gutter-md">
        <div v-for="(item, index) in saleItems" :key="index" class="row items-center q-mb-md">
          <q-select
  v-model="item.product"
  label="Select Product"
  :options="filteredProducts"
  option-value="id"
  option-label="name"
  dense
  outlined
  class="col-7 q-mr-sm"
  use-input
  input-debounce="300"
  @filter="filterProducts"
/>

          <q-input
            v-model="item.quantity"
            label="Qty"
            type="number"
            dense
            outlined
            class="col-3"
          />
          <q-btn v-if="saleItems.length > 1" @click="removeProductRow(index)" round flat icon="close" color="negative" />
        </div>

        <q-btn 
          flat 
          icon="add" 
          color="primary" 
          label="Add Another Product" 
          @click="addProductRow"
        />

        <!-- Total Price Display -->
        <div class="total-price-container">
          <span>Total Price:</span>
          <strong class="total-price">GHS {{ totalPrice }}</strong>
        </div>
      </q-card-section>

      <!-- Actions -->
      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey" @click="emit('update:modelValue', false)" />
        <q-btn label="Confirm Sale" color="primary" @click="recordSale"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style scoped>
/* Dialog Card Styling */
.q-dialog-card {
  width: 600px;
  max-width: 90vw;
  border-radius: 12px;
}

/* Total Price Styling */
.total-price-container {
  display: flex;
  justify-content: space-between;
  font-size: 18px;
  padding: 10px 0;
  color: #444;
}

.total-price {
  color: #0288d1;
  font-weight: bold;
}

/* Button Hover Effects */
.q-btn {
  transition: all 0.2s ease-in-out;
}

.q-btn:hover {
  transform: scale(1.05);
}
</style>
