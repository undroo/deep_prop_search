export const textStyles = {
  // Headings
  heading: {
    primary: 'text-3xl font-bold text-gray-900',
    secondary: 'text-2xl font-semibold text-gray-900',
    tertiary: 'text-xl font-semibold text-gray-900',
  },
  
  // Body text
  body: {
    regular: 'text-gray-800',
    light: 'text-gray-600',
    muted: 'text-gray-500',
  },
  
  // Labels and small text
  label: {
    regular: 'text-sm font-medium text-gray-800',
    light: 'text-sm text-gray-600',
  },
  
  // Icons
  icon: {
    regular: 'text-gray-800',
    light: 'text-gray-600',
    colored: {
      work: 'text-blue-500 text-xl',
      groceries: 'text-green-500 text-xl',
      schools: 'text-purple-500 text-xl',
    }
  },
  
  // Table styles
  table: {
    container: 'overflow-x-auto',
    wrapper: 'min-w-full bg-white',
    header: {
      row: 'bg-gray-50',
      cell: 'py-2 px-4 text-left text-sm font-medium text-gray-800',
    },
    body: {
      row: 'border-b border-gray-200',
      cell: 'py-3 px-4 text-sm text-gray-800',
    }
  },
  
  // Section headers
  section: {
    container: 'flex items-center space-x-2 mb-4',
    header: 'text-xl font-semibold text-gray-900',
  },

  // Layout
  layout: {
    container: 'space-y-6',
    section: 'space-y-4',
  }
}; 