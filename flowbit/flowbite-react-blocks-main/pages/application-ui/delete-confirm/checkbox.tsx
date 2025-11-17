import { Button, Checkbox, Label, Modal } from "flowbite-react";
import type { FC } from "react";
import { useState } from "react";

const ConfirmDeleteWithCheckbox: FC = function () {
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
        <Modal.Body className="relative p-4 bg-white rounded-lg shadow dark:bg-gray-800 sm:p-5">
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
          <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
            Remove 15 items?
          </h3>
          <p className="mb-4 text-gray-500 dark:text-gray-400">
            If you remove them, it may delete these questions account and
            activity. These questions can also no longer request info about you
            on Flowbite.
          </p>
          <div
            className="p-4 mb-4 text-sm text-left text-gray-500 bg-gray-100 rounded-lg sm:mb-5 dark:bg-gray-700 dark:text-gray-400"
            role="alert"
          >
            <div className="flex">
              <Checkbox
                id="confirm-checkbox"
                className="mt-1 w-4 h-4 bg-gray-50 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                required
              />
              <Label
                htmlFor="confirm-checkbox"
                className="text-gray-500 ml-2 text-sm dark:text-gray-400"
              >
                Also delete&nbsp;
                <span className="font-medium text-gray-900 dark:text-white">
                  all posts, photos and videos
                </span>
                &nbsp;on Flowbite that 15 questions may have published on your
                behalf.
              </Label>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              color="gray"
              onClick={() => setShowModal(false)}
              outline
              className="[&>span]:text-gray-500 focus:ring-blue-300 hover:!text-gray-900 dark:!bg-gray-700 dark:[&>span]:bg-gray-700 dark:[&>span]:text-gray-300 dark:hover:!text-white dark:hover:!bg-gray-600 dark:focus:ring-gray-600"
            >
              Cancel
            </Button>
            <Button
              color="failure"
              type="submit"
              size="sm"
              className="[&>span]:items-center"
            >
              <svg
                aria-hidden
                className="w-4 h-4 mr-1.5 -ml-1"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fillRule="evenodd"
                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              Yes, delete
            </Button>
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default ConfirmDeleteWithCheckbox;
