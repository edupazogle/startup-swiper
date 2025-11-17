import { Button, Label, Modal, TextInput } from "flowbite-react";
import type { FC } from "react";
import { useState } from "react";

const DeleteConfirmationWithInputField: FC = function () {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <Button onClick={() => setShowModal(true)} className="mx-auto">
        Show delete confirmation
      </Button>
      <Modal
        onClose={() => setShowModal(false)}
        popup
        size="md"
        show={showModal}
      >
        <Modal.Body className="p-0 relative bg-white rounded-lg shadow dark:bg-gray-800">
          <div className="flex justify-between items-center py-4 px-4 sm:px-5">
            <h3 className="text-lg font-semibold leading-none text-gray-900 dark:text-white">
              Are you sure?
            </h3>
            <button
              onClick={() => setShowModal(false)}
              className="text-gray-400 absolute top-2.5 right-2.5 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-600 dark:hover:text-white"
            >
              <svg
                aria-hidden
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
                className="w-5 h-5"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="sr-only">Close modal</span>
            </button>
          </div>
          <p className="py-4 px-4 text-orange-700 bg-orange-100 border-t border-b border-orange-200 sm:px-5 dark:border-gray-600 dark:bg-gray-700 dark:text-orange-300">
            Unexpected bad things can happen if you don’t read this!
          </p>
          <div className="py-4 px-4 sm:px-5 sm:py-5">
            <p className="text-gray-500 dark:text-gray-400">
              This action&nbsp;
              <span className="font-semibold text-gray-900 dark:text-white">
                CANNOT
              </span>
              &nbsp;be undone. This will permanently delete the&nbsp;
              <span className="font-semibold text-gray-900 dark:text-white">
                bergside/flowbite-library
              </span>
              &nbsp;file, wiki, issues and comments, and remove all collaborator
              assosiations.
            </p>
            <form>
              <div className="mt-2 mb-4">
                <Label
                  htmlFor="repository-name-input"
                  className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                >
                  Please type in the name of the repository to confirm.
                </Label>
                <TextInput
                  id="repository-name-input"
                  placeholder="Ex. bergside/flowbite-library"
                  required
                />
              </div>
              <Button color="failure" type="submit" size="sm" className="w-full">
                I understand, delete this repository
              </Button>
            </form>
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default DeleteConfirmationWithInputField;
