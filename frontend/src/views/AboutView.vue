<template>
  <div class="about">
    <h1>About Page</h1>
    <h3>Coming soon...</h3>
  </div>
</template>
<style scoped>
.about {
  padding-top: 5rem;
  color: #fff;
}

.about h3{
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}


</style>
