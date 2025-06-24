export default function AccountsPage() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">Accounts</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your bank accounts and view balances.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            type="button"
            className="btn-primary"
          >
            Create Account
          </button>
        </div>
      </div>
      <div className="mt-8">
        <div className="card">
          <div className="card-body">
            <p className="text-gray-500 text-center py-8">
              No accounts found. Create your first account to get started.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
