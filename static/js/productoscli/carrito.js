const Clickbutton = document.querySelectorAll('.button'); /*Boton para iniciar la acccion*/

Clickbutton.forEach(btn => {
    btn.addEventListener('click', addToCarritoItem);
});

function addToCarritoItem(e) {
    const button = e.target;
    const item = button.closest('.card');
    const itemTitle = item.querySelector('.card-title').textContent;
    const itemPrice = item.querySelector('.card-price span').textContent;
    const itemImg = item.querySelector('.card-img-top').src;

    const newItem = {
        title: itemTitle,
        price: itemPrice,
        img: itemImg,
        cantidad: 1
    };

    addItemCarrito(newItem);
}

function addItemCarrito(newItem) {
    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    const index = carrito.findIndex(item => item.title.trim() === newItem.title.trim());
    if (index !== -1) {
        carrito[index].cantidad += 1;
    } else {
        carrito.push(newItem);
    }

    localStorage.setItem('carrito', JSON.stringify(carrito));
}

document.addEventListener('DOMContentLoaded', () => { /* Ver el producto en carrito*/
    const tbody = document.querySelector('.tbody');
    if (!tbody) return;

    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    tbody.innerHTML = '';
    carrito.forEach(item => {
        const tr = document.createElement('tr');
        tr.classList.add('ItemCarrito');
        const Content = `
            <td class="table-imagen td">
                <img src="${item.img}" alt="">
            </td>
            <td class="table-productos td">
                <h2 class="card-title">${item.title}</h2>
            </td>
            <td class="table__price td"> 
                <h6 class="card-price"><span>${item.price}</span></h6>
            </td>
            <td class="table__cantidad td">
                <input type="number" min="1" value="${item.cantidad}">
                <button class="delete btn btn-danger">X</button>
            </td>
        `;
        tr.innerHTML = Content;
        tbody.append(tr);
    });
});