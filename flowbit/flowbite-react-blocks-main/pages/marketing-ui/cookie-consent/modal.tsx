import { Button, Modal } from "flowbite-react";
import type { FC } from "react";
import { useState } from "react";
import FlowbiteLogoSVG from "../../../components/flowbite-logo";

const CookieConsentModal: FC = function () {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button onClick={() => setShow(true)}>Show cookie consent modal</Button>
      <Modal show={show}>
        <Modal.Header>
          <a
            href="#"
            className="mb-2 flex items-center text-xl font-semibold text-gray-900 dark:text-white sm:mb-0"
          >
            <FlowbiteLogoSVG />
            Flowbite
          </a>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-6 text-gray-500 dark:text-gray-400">
            <p className="mb-4 text-2xl font-bold text-gray-900 dark:text-white">
              Before continuing on our website
            </p>
            <p className="mb-2">Flowbite uses cookies and data to:</p>
            <ul className="mb-4 list-disc space-y-2 pl-4">
              <li>
                Provide and manage services, for example to monitor service
                interruptions and protect you from spam, fraudulent and illegal
                activities.
              </li>
              <li>
                Measure audience engagement and site statistics to understand
                how our services are used.
              </li>
            </ul>
            <p>
              Click "Customize" to review options, such as settings to reject
              the use of cookies for personalization and browser-level
              information about settings to reject some or all cookies for other
              uses. You can also visit g.co/privacytools at any time.
            </p>
          </div>
          <div className="items-center justify-between space-y-4 pt-0 sm:flex sm:space-y-0">
            <div className="items-center space-y-4 sm:flex sm:space-x-4 sm:space-y-0">
              <Button onClick={() => setShow(false)}>I accept</Button>
              <Button color="gray" onClick={() => setShow(false)} outline>
                Block cookies
              </Button>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              <a href="#" className="hover:underline">
                Privacy
              </a>
              <div className="h-1.5 w-1.5 rounded-full bg-gray-400"></div>
              <a href="#" className="hover:underline">
                Terms
              </a>
            </div>
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default CookieConsentModal;
