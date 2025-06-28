
  document.addEventListener('DOMContentLoaded', () => {
    const toastEl = document.getElementById('welcomeToast');

    // Verificar si ya se mostró el toast en esta sesión
    if (!sessionStorage.getItem('welcome_shown')) {
      const toast = new bootstrap.Toast(toastEl, {
        delay: 5000
      });
      toast.show();

      // Marcar que ya se mostró
      sessionStorage.setItem('welcome_shown', 'true');
    }
  });