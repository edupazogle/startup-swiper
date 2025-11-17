import { Button, Modal } from "flowbite-react";
import type { FC } from "react";
import { useState } from "react";

const CookieConsentPopup: FC = function () {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button onClick={() => setShow(true)}>Show cookie consent popup</Button>
      <Modal popup position="bottom-right" show={show}>
        <Modal.Body>
          <div className="py-5 text-sm text-gray-500 dark:text-gray-400">
            <p className="mb-2">
              We use cookies, including third party cookies, for operational
              purposes, statistical analyses, to personalize your experience,
              provide you with targeted content tailored to your interests and
              to analyze the performance of our advertising campaigns.
            </p>
            <p>
              To find out more about the types of cookies, as well as who sends
              them on our website, please visit our dedicated guide to&nbsp;
              <a
                href="#"
                className="font-medium text-gray-900 hover:underline dark:text-white"
              >
                managing cookies
              </a>
              .
            </p>
          </div>
          <div className="items-center justify-between space-y-4 pt-0 sm:flex sm:space-y-0">
            <Button onClick={() => setShow(false)}>
              Personalize my choices
            </Button>
            <div className="items-center space-y-4 sm:flex sm:space-x-4 sm:space-y-0">
              <Button color="gray" onClick={() => setShow(false)} outline>
                Reject all
              </Button>
              <Button onClick={() => setShow(false)}>Accept all</Button>
            </div>
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default CookieConsentPopup;
