import React, { useState, useEffect } from 'react';
import { Plus, X, Save, Settings } from 'lucide-react';

interface SemesterManagerProps {
  isOpen: boolean;
  onClose: () => void;
  currentSemesters: string[];
  onSave: (semesters: string[]) => void;
}

const SemesterManager: React.FC<SemesterManagerProps> = ({ 
  isOpen, 
  onClose, 
  currentSemesters = [], 
  onSave 
}) => {
  const [semesters, setSemesters] = useState<string[]>(currentSemesters);
  const [newSemester, setNewSemester] = useState('');

  useEffect(() => {
    console.log('SemesterManager received currentSemesters:', currentSemesters); // Debug log
    setSemesters(currentSemesters);
  }, [currentSemesters]);

  const addSemester = () => {
    if (newSemester.trim() && !semesters.includes(newSemester.trim())) {
      setSemesters([...semesters, newSemester.trim()]);
      setNewSemester('');
    }
  };

  const removeSemester = (index: number) => {
    setSemesters(semesters.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    onSave(semesters);
    onClose();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      addSemester();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Settings className="h-5 w-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">
                Manage Allowed Semesters
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add New Semester
            </label>
            <div className="flex">
              <input
                type="text"
                value={newSemester}
                onChange={(e) => setNewSemester(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., BS (SE) - 5C or 7A"
                className="flex-1 block w-full rounded-l-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
              <button
                onClick={addSemester}
                disabled={!newSemester.trim()}
                className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Examples: "BS (SE) - 5C", "MS (CS) - 1A", "7A", "3B"
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Semesters ({semesters.length})
            </label>
            <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-md">
              {semesters.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No semesters configured. Add some semesters above.
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {semesters.map((semester, index) => (
                    <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50">
                      <span className="text-sm text-gray-900">{semester}</span>
                      <button
                        onClick={() => removeSemester(index)}
                        className="text-red-600 hover:text-red-800"
                        title="Remove semester"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default SemesterManager;