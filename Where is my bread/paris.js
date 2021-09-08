const openTicketButtons = document.querySelectorAll('[data-ticket-target]')
const closeTicketButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')

openTicketButtons.forEach(button => {
  button.addEventListener('click', () => {
    const ticket = document.querySelector(button.dataset.ticketTarget)
    openTicket(ticket)
  })
})

overlay.addEventListener('click', () => {
  const tickets = document.querySelectorAll('.ticket.active')
  tickets.forEach(ticket => {
    closeTicket(ticket)
  })
})

closeTicketButtons.forEach(button => {
  button.addEventListener('click', () => {
    const ticket = button.closest('.ticket')
    closeTicket(ticket)
  })
})

function openTicket(ticket) {
  if (ticket == null) return
  ticket.classList.add('active')
  overlay.classList.add('active')
}

function closeTicket(ticket) {
  if (ticket == null) return
  ticket.classList.remove('active')
  overlay.classList.remove('active')
}