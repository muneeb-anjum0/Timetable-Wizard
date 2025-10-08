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
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <img src="/setting.svg" alt="Setting" className="h-6 w-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900 tracking-tight">
                Manage Allowed Semesters
              </h3>
            </div>
            <button
              onClick={onClose}
              className="rounded-full p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition"
              title="Close"
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
                className="flex-1 block w-full rounded-l-full border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2"
              />
              <button
                onClick={addSemester}
                disabled={!newSemester.trim()}
                className="inline-flex items-center px-3 py-2 border-2 border-blue-400 rounded-full bg-white text-blue-600 hover:bg-blue-50 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed ml-2"
                title="Add semester"
              >
                <img src="/add.svg" alt="Add" className="h-4 w-4" />
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
            <div className="max-h-48 overflow-y-auto border border-gray-100 rounded-xl bg-gray-50">
              {semesters.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  No semesters configured. Add some semesters above.
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {semesters.map((semester, index) => (
                    <div key={index} className="flex items-center justify-between p-3 hover:bg-blue-50 rounded-xl">
                      <span className="text-sm text-gray-900">{semester}</span>
                      <button
                        onClick={() => removeSemester(index)}
                        className="inline-flex items-center px-2 py-1 border-2 border-red-400 rounded-full bg-white text-red-600 hover:bg-red-50 hover:text-red-800 transition"
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

        <div className="px-6 py-4 border-t border-gray-100 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="inline-flex items-center px-4 py-2 border-2 border-gray-400 text-xs sm:text-sm font-medium rounded-full shadow text-gray-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="inline-flex items-center px-4 py-2 border-2 border-blue-400 text-xs sm:text-sm font-medium rounded-full shadow text-blue-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 transition"
          >
            <img src="/add.svg" alt="Save" className="h-4 w-4 mr-2" />
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default SemesterManager;