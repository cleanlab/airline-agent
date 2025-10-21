"use client";

import "@copilotkit/react-ui/styles.css";
import { CopilotChat } from "@copilotkit/react-ui";
import { useRenderToolCall } from "@copilotkit/react-core"
import { ToolRender } from "@/components/ToolRender";

export default function YourApp() {
    useRenderToolCall({
        name: "*",
        render: (props: { args: any; status: string; result: any; name: string }) => <ToolRender {...props} />,
    });

    return (
        <main>
            <CopilotChat disableSystemMessage />
        </main>
    );
}
