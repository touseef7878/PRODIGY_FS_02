// Employee Management System Frontend
class EmployeeManagement {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
        this.token = localStorage.getItem('token');
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.currentEmployee = null;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthentication();
    }

    bindEvents() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });

        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // Employee form
        document.getElementById('employee-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addEmployee();
        });

        // Clear form button
        document.getElementById('clear-form').addEventListener('click', () => {
            this.clearForm();
        });

        // Search and filters
        document.getElementById('search-input').addEventListener('input', 
            this.debounce(() => this.loadEmployees(), 500)
        );
        document.getElementById('department-filter').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadEmployees();
        });
        document.getElementById('status-filter').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadEmployees();
        });

        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadEmployees();
            }
        });
        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadEmployees();
        });

        // Modal events
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal();
            });
        });

        // Employee modal buttons
        document.getElementById('edit-employee-btn').addEventListener('click', () => {
            this.editEmployee();
        });
        document.getElementById('save-employee-btn').addEventListener('click', () => {
            this.saveEmployee();
        });
        document.getElementById('cancel-edit-btn').addEventListener('click', () => {
            this.cancelEdit();
        });
        document.getElementById('delete-employee-btn').addEventListener('click', () => {
            this.deleteEmployee();
        });

        // Upload events
        document.getElementById('profile-upload').addEventListener('change', (e) => {
            this.previewImage(e.target.files[0]);
        });
        document.getElementById('upload-btn').addEventListener('click', () => {
            this.uploadProfilePicture();
        });

        // Upload area click
        document.querySelector('.upload-area').addEventListener('click', () => {
            document.getElementById('profile-upload').click();
        });

        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        });
    }

    checkAuthentication() {
        if (this.token) {
            this.showDashboard();
        } else {
            this.showLogin();
        }
    }

    showLogin() {
        document.getElementById('login-section').classList.remove('hidden');
        document.getElementById('dashboard-section').classList.add('hidden');
    }

    showDashboard() {
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('dashboard-section').classList.remove('hidden');
        this.loadDashboardData();
    }

    async login() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('login-error');

        try {
            this.showLoading();
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username_or_email: username,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                localStorage.setItem('token', this.token);
                document.getElementById('admin-name').textContent = data.admin.username;
                this.showDashboard();
                errorDiv.classList.add('hidden');
            } else {
                errorDiv.textContent = data.message || 'Login failed';
                errorDiv.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Login error:', error);
            errorDiv.textContent = 'Network error. Please try again.';
            errorDiv.classList.remove('hidden');
        } finally {
            this.hideLoading();
        }
    }

    logout() {
        localStorage.removeItem('token');
        this.token = null;
        this.showLogin();
        document.getElementById('login-form').reset();
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show corresponding content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        const tabContent = document.getElementById(`${tabName}-tab`);
        tabContent.classList.add('active');
        tabContent.scrollIntoView({ behavior: 'smooth' });

        // Load data based on tab
        switch(tabName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'employees':
                this.loadEmployees();
                break;
            case 'add-employee':
                this.clearForm();
                break;
        }
    }

    async loadDashboardData() {
        try {
            const response = await this.makeRequest('/employees/stats');
            if (response.ok) {
                const data = await response.json();
                this.updateDashboardStats(data);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    updateDashboardStats(stats) {
        document.getElementById('total-employees').textContent = stats.total_employees || 0;
        document.getElementById('active-employees').textContent = stats.active_employees || 0;
        document.getElementById('inactive-employees').textContent = stats.inactive_employees || 0;
        document.getElementById('deleted-employees').textContent = stats.deleted_employees || 0;

        // Update department chart
        const chartContainer = document.getElementById('department-chart');
        chartContainer.innerHTML = '';

        if (stats.departments && stats.departments.length > 0) {
            stats.departments.forEach(dept => {
                const chartItem = document.createElement('div');
                chartItem.className = 'chart-item';
                chartItem.innerHTML = `
                    <h4>${dept.department}</h4>
                    <p>${dept.count}</p>
                `;
                chartContainer.appendChild(chartItem);
            });
        } else {
            chartContainer.innerHTML = '<p>No department data available</p>';
        }
    }

    async loadEmployees() {
        try {
            const search = document.getElementById('search-input').value;
            const department = document.getElementById('department-filter').value;
            const status = document.getElementById('status-filter').value;

            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage,
                ...(search && { search }),
                ...(department && { department }),
                ...(status && { status })
            });

            const response = await this.makeRequest(`/employees?${params}`);
            if (response.ok) {
                const data = await response.json();
                this.updateEmployeeTable(data.employees);
                this.updatePagination(data.pagination);
                this.updateDepartmentFilter(data.employees);
            }
        } catch (error) {
            console.error('Error loading employees:', error);
        }
    }

    updateEmployeeTable(employees) {
        const tbody = document.getElementById('employees-tbody');
        tbody.innerHTML = '';

        if (employees.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No employees found</td></tr>';
            return;
        }

        employees.forEach(employee => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    ${employee.profile_picture_path 
                        ? `<img src="${this.baseURL}/employees/${employee.id}/profile-picture" 
                             class="employee-photo" alt="${employee.name}" onerror="this.onerror=null;this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9IiNjY2NjY2MiPjxwYXRoIGQ9Ik0xMiA0YTIgMiAwIDAgMC0yIDJ2Mi41M2MtLjUxLjA3LS45OS4yNS0xLjQzLjUzYTEgMSAwIDAgMC0uMzIgMS4zNGMuMzYuNTguOTggMSAxLjc1IDFIMTJhMiAyIDAgMCAwIDAtNHYtLjUzYTIgMiAwIDAgMC0yLTJ6bTAgMTJhNCA0IDAgMCAwIDQtNCA0IDQgMCAwMC00IDR6bTAtMTBhNiA2IDAgMCAxIDYgNiA2IDYgMCAwMS02IDZ6Ii8+PC9zdmc+';">`
                        : `<div class="employee-photo-placeholder">
                             <i class="fas fa-user"></i>
                           </div>`}
                </td>
                <td>${employee.name}</td>
                <td>${employee.email}</td>
                <td>${employee.department}</td>
                <td>${employee.position}</td>
                <td>$${parseFloat(employee.salary).toLocaleString()}</td>
                <td>
                    <span class="status-badge ${employee.status === 'Active' ? 'status-active' : 'status-inactive'}">
                        ${employee.status}
                    </span>
                </td>
                <td>
                    <div class="employee-actions">
                        <button class="btn btn-sm btn-primary" onclick="app.viewEmployee(${employee.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="app.showUploadModal(${employee.id})">
                            <i class="fas fa-camera"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updatePagination(pagination) {
        document.getElementById('page-info').textContent = 
            `Page ${pagination.page} of ${pagination.pages}`;
        
        document.getElementById('prev-page').disabled = !pagination.has_prev;
        document.getElementById('next-page').disabled = !pagination.has_next;
    }

    updateDepartmentFilter(employees) {
        const filter = document.getElementById('department-filter');
        const currentValue = filter.value;
        const departments = [...new Set(employees.map(emp => emp.department))];
        
        // Keep existing options and add new ones
        const existingOptions = Array.from(filter.options).map(opt => opt.value).slice(1);
        const newDepartments = departments.filter(dept => !existingOptions.includes(dept));
        
        newDepartments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            filter.appendChild(option);
        });
        
        filter.value = currentValue;
    }

    async addEmployee() {
        const messageDiv = document.getElementById('form-message');

        try {
            // Get form data with validation
            let formData;
            try {
                formData = this.getFormData();
            } catch (validationError) {
                this.showMessage(messageDiv, validationError.message, 'error');
                return;
            }

            this.showLoading();
            const response = await this.makeRequest('/employees', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.showMessage(messageDiv, 'Employee added successfully!', 'success');
                this.clearForm();
                // Switch to employees tab and reload
                this.switchTab('employees');
            } else {
                let errorMsg = data.message || 'Failed to add employee';
                if (data.errors && Array.isArray(data.errors)) {
                    errorMsg += '\n' + data.errors.join('\n');
                }
                this.showMessage(messageDiv, errorMsg, 'error');
            }
        } catch (error) {
            console.error('Add employee error:', error);
            this.showMessage(messageDiv, 'Network error. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    getFormData() {
        const salaryValue = document.getElementById('emp-salary').value;
        const hireDateValue = document.getElementById('emp-hire-date').value;
        
        // Validate required fields
        if (!salaryValue) {
            throw new Error('Salary is required');
        }
        
        if (!hireDateValue) {
            throw new Error('Hire date is required');
        }
        
        return {
            name: document.getElementById('emp-name').value.trim(),
            email: document.getElementById('emp-email').value.trim().toLowerCase(),
            phone: document.getElementById('emp-phone').value.trim() || null,
            address: document.getElementById('emp-address').value.trim() || null,
            department: document.getElementById('emp-department').value.trim(),
            position: document.getElementById('emp-position').value.trim(),
            salary: parseFloat(salaryValue),
            hire_date: hireDateValue,
            status: document.getElementById('emp-status').value.trim()
        };
    }

    clearForm() {
        document.getElementById('employee-form').reset();
        document.getElementById('form-message').classList.add('hidden');
    }

    async viewEmployee(id) {
        try {
            const response = await this.makeRequest(`/employees/${id}`);
            if (response.ok) {
                const data = await response.json();
                this.currentEmployee = data.employee;
                this.showEmployeeModal(data.employee);
            }
        } catch (error) {
            console.error('Error loading employee:', error);
        }
    }

    showEmployeeModal(employee) {
        const modal = document.getElementById('employee-modal');
        const detailsDiv = document.getElementById('employee-details');
        
        detailsDiv.innerHTML = `
            <div class="employee-detail">
                <div>
                    ${employee.profile_picture_path 
                        ? `<img src="${this.baseURL}/employees/${employee.id}/profile-picture" 
                             class="employee-detail-photo" alt="${employee.name}" onerror="this.onerror=null;this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9IiNjY2NjY2MiPjxwYXRoIGQ9Ik0xMiA0YTIgMiAwIDAgMC0yIDJ2Mi41M2MtLjUxLjA3LS45OS4yNS0xLjQzLjUzYTEgMSAwIDAgMC0uMzIgMS4zNGMuMzYuNTguOTggMSAxLjc1IDFIMTJhMiAyIDAgMCAwIDAtNHYtLjUzYTIgMiAwIDAgMC0yLTJ6bTAgMTJhNCA0IDAgMCAwIDQtNCA0IDQgMCAwMC00IDR6bTAtMTBhNiA2IDAgMCAxIDYgNiA2IDYgMCAwMS02IDZ6Ii8+PC9zdmc+';">`
                        : `<div class="employee-detail-photo-placeholder">
                             <i class="fas fa-user"></i>
                           </div>`}
                </div>
                <div class="employee-detail-info">
                    <h3>${employee.name}</h3>
                    <p>${employee.position}</p>
                    <p>${employee.department}</p>
                    <p>
                        <span class="status-badge ${employee.status === 'Active' ? 'status-active' : 'status-inactive'}">
                            ${employee.status}
                        </span>
                    </p>
                </div>
            </div>
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Email:</label>
                    <span>${employee.email}</span>
                </div>
                <div class="detail-item">
                    <label>Phone:</label>
                    <span>${employee.phone || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <label>Salary:</label>
                    <span>$${parseFloat(employee.salary).toLocaleString()}</span>
                </div>
                <div class="detail-item">
                    <label>Hire Date:</label>
                    <span>${new Date(employee.hire_date).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="detail-item">
                <label>Address:</label>
                <span>${employee.address || 'N/A'}</span>
            </div>
        `;

        modal.classList.remove('hidden');
        this.resetModalButtons();
    }

    resetModalButtons() {
        document.getElementById('edit-employee-btn').classList.remove('hidden');
        document.getElementById('save-employee-btn').classList.add('hidden');
        document.getElementById('cancel-edit-btn').classList.add('hidden');
        document.getElementById('delete-employee-btn').classList.remove('hidden');
        document.getElementById('employee-details').classList.remove('hidden');
        document.getElementById('edit-employee-form').classList.add('hidden');
    }

    editEmployee() {
        const employee = this.currentEmployee;
        const editFormDiv = document.getElementById('edit-employee-form');
        
        editFormDiv.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <label for="edit-name">Full Name *</label>
                    <input type="text" id="edit-name" value="${employee.name}" required>
                </div>
                <div class="form-group">
                    <label for="edit-email">Email *</label>
                    <input type="email" id="edit-email" value="${employee.email}" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="edit-phone">Phone</label>
                    <input type="tel" id="edit-phone" value="${employee.phone || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-department">Department *</label>
                    <input type="text" id="edit-department" value="${employee.department}" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="edit-position">Position *</label>
                    <input type="text" id="edit-position" value="${employee.position}" required>
                </div>
                <div class="form-group">
                    <label for="edit-salary">Salary *</label>
                    <input type="number" id="edit-salary" value="${employee.salary}" step="0.01" required>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="edit-hire-date">Hire Date *</label>
                    <input type="date" id="edit-hire-date" value="${employee.hire_date}" required>
                </div>
                <div class="form-group">
                    <label for="edit-status">Status</label>
                    <select id="edit-status">
                        <option value="Active" ${employee.status === 'Active' ? 'selected' : ''}>Active</option>
                        <option value="Inactive" ${employee.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                    </select>
                </div>
            </div>
            <div class="form-group full-width">
                <label for="edit-address">Address</label>
                <textarea id="edit-address" rows="3">${employee.address || ''}</textarea>
            </div>
        `;

        // Show edit form, hide details
        document.getElementById('employee-details').classList.add('hidden');
        editFormDiv.classList.remove('hidden');
        
        // Update buttons
        document.getElementById('edit-employee-btn').classList.add('hidden');
        document.getElementById('save-employee-btn').classList.remove('hidden');
        document.getElementById('cancel-edit-btn').classList.remove('hidden');
        document.getElementById('delete-employee-btn').classList.add('hidden');
    }

    async saveEmployee() {
        const employee = this.currentEmployee;
        const formData = {
            name: document.getElementById('edit-name').value,
            email: document.getElementById('edit-email').value,
            phone: document.getElementById('edit-phone').value || null,
            address: document.getElementById('edit-address').value || null,
            department: document.getElementById('edit-department').value,
            position: document.getElementById('edit-position').value,
            salary: parseFloat(document.getElementById('edit-salary').value),
            hire_date: document.getElementById('edit-hire-date').value,
            status: document.getElementById('edit-status').value
        };

        try {
            this.showLoading();
            const response = await this.makeRequest(`/employees/${employee.id}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.currentEmployee = data.employee;
                this.showEmployeeModal(data.employee);
                this.loadEmployees(); // Refresh the list
            } else {
                alert(data.message || 'Failed to update employee');
            }
        } catch (error) {
            console.error('Save employee error:', error);
            alert('Network error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    cancelEdit() {
        this.showEmployeeModal(this.currentEmployee);
    }

    async deleteEmployee() {
        if (!confirm('Are you sure you want to delete this employee? This action can be undone later.')) {
            return;
        }

        const employee = this.currentEmployee;

        try {
            this.showLoading();
            const response = await this.makeRequest(`/employees/${employee.id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.closeModal();
                this.loadEmployees(); // Refresh the list
            } else {
                const data = await response.json();
                alert(data.message || 'Failed to delete employee');
            }
        } catch (error) {
            console.error('Delete employee error:', error);
            alert('Network error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showUploadModal(employeeId) {
        this.currentEmployeeId = employeeId;
        document.getElementById('upload-modal').classList.remove('hidden');
        document.getElementById('upload-preview').classList.add('hidden');
        document.getElementById('profile-upload').value = '';
    }

    previewImage(file) {
        if (!file) return;

        const preview = document.getElementById('upload-preview');
        const previewImg = document.getElementById('preview-image');
        
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }

    async uploadProfilePicture() {
        const fileInput = document.getElementById('profile-upload');
        const file = fileInput.files[0];

        if (!file) {
            alert('Please select a file first');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading();
            const response = await fetch(`${this.baseURL}/employees/${this.currentEmployeeId}/upload-profile`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.closeModal();
                this.loadEmployees(); // Refresh the list
                if (this.currentEmployee && this.currentEmployee.id === this.currentEmployeeId) {
                    this.viewEmployee(this.currentEmployeeId); // Refresh modal if open
                }
            } else {
                alert(data.message || 'Failed to upload image');
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Network error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    async makeRequest(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            }
        };

        const requestOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {})
            }
        };

        const response = await fetch(`${this.baseURL}${endpoint}`, requestOptions);

        // Handle token expiration
        if (response.status === 401) {
            this.logout();
            return;
        }

        return response;
    }

    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    showMessage(element, message, type) {
        element.textContent = message;
        element.className = `message ${type}`;
        element.classList.remove('hidden');

        // Auto hide after 5 seconds
        setTimeout(() => {
            element.classList.add('hidden');
        }, 5000);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EmployeeManagement();
});