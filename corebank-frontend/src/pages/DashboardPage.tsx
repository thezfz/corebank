export default function DashboardPage() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">欢迎使用数脉银行</h1>
          <p className="text-gray-600">您的安全银行仪表板</p>
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="card">
              <div className="card-body text-center">
                <h3 className="text-lg font-medium text-gray-900">总余额</h3>
                <p className="text-2xl font-bold text-primary-600">¥0.00</p>
              </div>
            </div>
            <div className="card">
              <div className="card-body text-center">
                <h3 className="text-lg font-medium text-gray-900">账户数量</h3>
                <p className="text-2xl font-bold text-primary-600">0</p>
              </div>
            </div>
            <div className="card">
              <div className="card-body text-center">
                <h3 className="text-lg font-medium text-gray-900">交易记录</h3>
                <p className="text-2xl font-bold text-primary-600">0</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
