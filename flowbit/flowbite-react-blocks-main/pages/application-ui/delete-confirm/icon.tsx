import { Button, Modal } from "flowbite-react";
import type { FC } from "react";
import { useState } from "react";

const DeleteConfirmationWithIcon: FC = function () {
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
        <Modal.Body className="relative p-4 text-center bg-white rounded-lg shadow dark:bg-gray-800 sm:p-5">
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
          <div className="flex justify-center items-center p-2 mx-auto mb-4 w-12 h-12 bg-gray-100 rounded-lg dark:bg-gray-700">
            <svg
              aria-hidden
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
              className="w-8 h-8 text-gray-500 dark:text-gray-400"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <p className="text-gray-900 dark:text-white mb-3.5">
            <span className="text-blue-600 dark:text-blue-500">@bonniegr</span>,
            are you sure you want to delete this product from platform?
          </p>
          <p className="mb-4 text-gray-500 dark:text-gray-300">
            This action cannot be undone.
          </p>
          <div className="flex justify-center items-center space-x-4">
            <Button
              color="gray"
              onClick={() => setShowModal(false)}
              outline
              size="sm"
              className="[&>span]:text-gray-500 focus:ring-blue-300 hover:!text-gray-900 dark:!bg-gray-700 dark:[&>span]:bg-gray-700 dark:[&>span]:text-gray-300 dark:hover:!text-white dark:hover:!bg-gray-600 dark:focus:ring-gray-600"
            >
              No, cancel
            </Button>
            <Button color="failure" type="submit">
              Yes, delete
            </Button>
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default DeleteConfirmationWithIcon;
