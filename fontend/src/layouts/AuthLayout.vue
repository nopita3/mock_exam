<template>
  <div class="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#EBEBEB] p-4">
    <div class="absolute -top-24 -left-24 h-80 w-80 rounded-full bg-[#7A2123]/15 blur-3xl"></div>
    <div class="absolute -bottom-32 -right-24 h-96 w-96 rounded-full bg-[#231F20]/10 blur-3xl"></div>
    <div class="relative z-10">
      <slot />
    </div>
  </div>
</template>
