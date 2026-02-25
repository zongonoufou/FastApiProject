const API_BASE_URL = 'http://127.0.0.1:8000';

// Éléments DOM
const userForm = document.getElementById('userForm');
const formMessage = document.getElementById('formMessage');
const userListDiv = document.getElementById('userList');
const refreshBtn = document.getElementById('refreshBtn');

// Fonction pour afficher un message
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    setTimeout(() => {
        element.textContent = '';
        element.className = 'message';
    }, 3000); 
}

// Fonction pour récupérer et afficher les utilisateurs
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/`);
        if (!response.ok) {
            throw new Error('Erreur lors du chargement des utilisateurs');
        }
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        console.error('Erreur:', error);
        userListDiv.innerHTML = '<p class="error">Impossible de charger les utilisateurs</p>';
    }
}

// Fonction pour afficher les utilisateurs
function displayUsers(users) {
    if (users.length === 0) {
        userListDiv.innerHTML = '<p>Aucun utilisateur trouvé.</p>';
        return;
    }

    let html = '';
    users.forEach(user => {
        html += `
            <div class="user-card">
                <h3>${user.name}</h3>
                <p><strong>Email :</strong> ${user.email}</p>
                <p><strong>Âge :</strong> ${user.age}</p>
                ${user.profile ? `
                    <div class="profile">
                        <p><strong>Bio :</strong> ${user.profile.bio || 'Non renseignée'}</p>
                        <p><strong>Avatar :</strong> ${user.profile.avatar_url ? `<a href="${user.profile.avatar_url}" target="_blank">Voir</a>` : 'Non renseigné'}</p>
                    </div>
                ` : ''}
            </div>
        `;
    });
    userListDiv.innerHTML = html;
}

// Gestionnaire de soumission du formulaire
userForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const age = parseInt(document.getElementById('age').value);

    const userData = { name, email, age };

    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erreur lors de la création');
        }

        const newUser = await response.json();
        showMessage(formMessage, 'Utilisateur créé avec succès !', 'success');
        userForm.reset();
        loadUsers(); // Recharger la liste
    } catch (error) {
        showMessage(formMessage, error.message, 'error');
    }
});

// Rafraîchir la liste
refreshBtn.addEventListener('click', loadUsers);

// Charger les utilisateurs au démarrage
loadUsers();