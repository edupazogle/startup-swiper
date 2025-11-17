import { Button, DarkThemeToggle, Flowbite, Navbar } from "flowbite-react";
import type { FC } from "react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";

const pages = import.meta.glob("./pages/**/*.tsx", { eager: true });
const routes = [];
for (const path of Object.keys(pages)) {
  const fileName = path.match(/\.\/pages\/(.*)\.tsx$/)?.[1];
  if (!fileName) {
    continue;
  }

  const normalizedPathName = fileName.includes("$")
    ? fileName.replace("$", ":")
    : fileName.replace(/\/index/, "");

  routes.push({
    path: fileName === "index" ? "/" : `/${normalizedPathName.toLowerCase()}`,
    // @ts-expect-error
    Element: pages[path].default,
    // @ts-expect-error
    loader: pages[path]?.loader as unknown as LoaderFunction | undefined,
    // @ts-expect-error
    action: pages[path]?.action as unknown as ActionFunction | undefined,
    // @ts-expect-error
    ErrorBoundary: pages[path]?.ErrorBoundary as unknown as JSX.Element,
  });
}

const router = createBrowserRouter(
  // eslint-disable-next-line no-unused-vars
  routes.map(({ Element, ErrorBoundary, ...props }) => ({
    ...props,
    element: <Element />,
  }))
);

const rootElem = document.getElementById("root");
if (!rootElem) {
  throw new Error("React root element doesn't exist");
}

const RootNavbar: FC = function () {
  return (
    <Navbar fluid rounded>
      <Navbar.Brand href="/">
        <img
          alt="Flowbite React Logo"
          src="https://flowbite.com/docs/images/logo.svg"
          className="mr-3 h-6 sm:h-9"
        />
        <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">
          Flowbite React
        </span>
      </Navbar.Brand>
      <div className="flex gap-2 md:order-2">
        <Button href="https://www.flowbite-react.com/docs/getting-started/introduction">Getting started</Button>
        <DarkThemeToggle />
        <Navbar.Toggle theme={{icon: "h-5 w-5 shrink-0"}} />
      </div>
      <Navbar.Collapse>
        <Navbar.Link active href="/">
          <p>Home</p>
        </Navbar.Link>
        <Navbar.Link href="https://www.flowbite-react.com/docs/getting-started/quickstart">
          Quickstart
        </Navbar.Link>
        <Navbar.Link href="https://www.flowbite-react.com/docs/customize/theme">
          Customize
        </Navbar.Link>
        <Navbar.Link href="https://flowbite.com/dashboard/downloads/">
          Pro resources
        </Navbar.Link>
        <Navbar.Link href="https://github.com/themesberg/flowbite-react">
          Github repo
        </Navbar.Link>
      </Navbar.Collapse>
    </Navbar>
  );
};

const root = createRoot(rootElem);
root.render(
  <StrictMode>
    <Flowbite
      theme={{
        theme: {
          navbar: {
            root: {
              base: "bg-white px-2 py-2.5 dark:border-gray-700 dark:bg-gray-800 sm:px-4 max-w-screen-2xl mx-auto dark:bg-gray-900",
            },
            collapse: {
              base: "w-full lg:block lg:w-auto",
            },
            link: {
              base: "block py-2 pr-4 pl-3 lg:p-0",
              active: {
                on: "bg-blue-700 text-white dark:text-white md:bg-transparent md:text-blue-700",
                off: "border-b border-gray-100 text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white lg:border-0 lg:hover:bg-transparent lg:hover:text-blue-700 lg:dark:hover:bg-transparent lg:dark:hover:text-white",
              },
              disabled: {
                on: "text-gray-400 hover:cursor-not-allowed dark:text-gray-600",
                off: "",
              },
            },
            toggle: {
              base: "inline-flex items-center rounded-lg p-2 text-sm text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600 lg:hidden",
              icon: "h-6 w-6 shrink-0",
            },
          },
          badge: {
            root: {
              color: {
                info: "bg-blue-100 text-blue-800 dark:bg-blue-200 dark:text-blue-800 group-hover:bg-blue-200 dark:group-hover:bg-blue-300",
              },
              size: {
                xs: "py-1 px-2 text-xs",
              },
            },
          },
          button: {
            color: {
              gray: "text-gray-900 bg-white border border-gray-200 enabled:hover:bg-gray-100 enabled:hover:text-blue-700 :ring-blue-700 focus:text-blue-700 dark:bg-transparent dark:text-gray-400 dark:border-gray-600 dark:enabled:hover:text-white dark:enabled:hover:bg-gray-700 focus:ring-2",
              info: "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
            },
            outline: {
              color: {
                gray: "border border-gray-200 dark:border-gray-500",
              },
            },
          },
          checkbox: {
            root: {
              base: "h-4 w-4 rounded border border-gray-300 bg-gray-100 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:ring-offset-gray-800 dark:focus:ring-blue-600 text-blue-600",
            },
          },
          progress: {
            color: {
              blue: "bg-blue-600",
            },
          },
          radio: {
            root: {
              base: "h-4 w-4 border border-gray-300 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:focus:bg-blue-600 dark:focus:ring-blue-600 text-blue-600",
            },
          },
          textInput: {
            field: {
              input: {
                colors: {
                  info: "border-blue-500 bg-blue-50 text-blue-900 placeholder-blue-700 focus:border-blue-500 focus:ring-blue-500 dark:border-blue-400 dark:bg-blue-100 dark:focus:border-blue-500 dark:focus:ring-blue-500",
                },
                withIcon: {
                  on: "!pl-12",
                },
              },
            },
          },
          toggleSwitch: {
            toggle: {
              checked: {
                color: {
                  blue: "bg-blue-700 border-blue-700",
                },
              },
            },
          },
        },
      }}
    >
      <RootNavbar />
      <RouterProvider router={router} />
    </Flowbite>
  </StrictMode>
);
