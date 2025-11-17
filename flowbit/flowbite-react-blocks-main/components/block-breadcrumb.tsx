import type { FC } from "react";
import { HiHome } from "react-icons/hi";
import type { BlockSectionProps } from "./block-section";
import { Breadcrumb } from "flowbite-react";

const BlockPageBreadcrumb: FC<
  Pick<BlockSectionProps, "title" | "description">
> = function ({ title, description }) {
  return (
    <div className="px-4 mb-6 flex flex-col gap-3 pt-6 max-w-screen-2xl mx-auto">
      <Breadcrumb>
        <Breadcrumb.Item href="/" icon={HiHome}>
          Blocks
        </Breadcrumb.Item>
        <Breadcrumb.Item>Marketing UI</Breadcrumb.Item>
        <Breadcrumb.Item>{title}</Breadcrumb.Item>
      </Breadcrumb>
      <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
        React {title} - Flowbite
      </h1>
      <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl">{description}</p>
      <hr className="dark:border-gray-800 border-gray-100 mt-4"/>
    </div>
  );
};

export default BlockPageBreadcrumb;
