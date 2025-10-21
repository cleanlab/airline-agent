import { useState } from "react";
import styles from "./ToolRender.module.css";

interface ToolRenderProps {
    args: any;
    status: string;
    result: any;
    name: string;
}

export function ToolRender({ args, status, result, name }: ToolRenderProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const isComplete = status === "complete";

    return (
        <div className={`${styles.container} ${isComplete ? styles.complete : styles.loading}`}>
            <div className={styles.header} onClick={() => setIsExpanded(!isExpanded)}>
                <div className={styles.headerLeft}>
                    <strong>{name}</strong>
                    {!isComplete && <span className={styles.spinner}></span>}
                </div>
                <span className={styles.arrow}>
                    {isExpanded ? "▼" : "▶"}
                </span>
            </div>

            {isExpanded && (
                <div className={styles.expandedContent}>
                    <div className={styles.section}>
                        <strong>Arguments:</strong>
                        <pre className={styles.codeBlock}>
                            {JSON.stringify(args, null, 2)}
                        </pre>
                    </div>
                    {isComplete && (
                        <div>
                            <strong>Result:</strong>
                            <pre className={styles.codeBlock}>
                                {JSON.stringify(result, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
