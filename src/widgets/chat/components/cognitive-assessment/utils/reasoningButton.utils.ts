import {
  REASONING_ICON_SVG,
  CHEVRON_ICON_SVG,
} from '@/shared/components/ui/icons/reasoningIcon'

function escapeHtmlAttribute(value: string): string {
    try {
        if (typeof value !== "string") {
            return "";
        }

        return value
            .replace(/&/g, "&amp;")
            .replace(/"/g, "&quot;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    } catch (error) {
        console.error("Failed to escape HTML attribute:", error);
        return "";
    }
}

// Handles optional whitespace around "=" and supports both single/double quoted values reliably.
// Escapes attribute names and ensures matching quote pairs to avoid malformed or partial matches.
function getAttributeValue(attrs: string, name: string): string | undefined {
    try {
        if (typeof attrs !== "string" || typeof name !== "string") {
            return undefined;
        }

        const escapedName = name.replace(
            /[.*+?^${}()|[\]\\]/g,
            "\\$&"
        );
        

        const match = attrs.match(
            new RegExp(`\\b${escapedName}\\s*=\\s*(['"])(.*?)\\1`, "i")
        );

        if (!match || match.length < 3) {
            return undefined;
        }

        return match?.[2];
    } catch (error) {
        console.error("Failed to extract attribute value:", error);
        return undefined;
    }
}
/*
Based on isInline attribute show either text or brain-icon(reasoningIconSvg), if isInline is not present - true (ByDefault)
<a isInline = "false"  -> show reasoningIcon
<a isInline = "true" -> inline Text
*/
export function injectReasoningButtons(html: string): string {
    try {
        if (typeof html !== "string" || !html.trim()) {
            return "";
        }

        return html.replace(
            /<a([^>]*?)data-cognitive-reasoning=["']([^"']+)["']([^>]*)>([\s\S]*?)<\/a>/gi,
            (_match, _before, reasoningId, _after, label) => {
                const htmlAttributes = `${_before} ${_after}`;
                const safeId = escapeHtmlAttribute(reasoningId);

                const isInline =
                    getAttributeValue(htmlAttributes, "isInline") === "false"
                        ? false
                        : true;

                const content =
                    !isInline || label.toLowerCase() === "source"
                        ? REASONING_ICON_SVG
                        : label;

                return `
                    <span
                      class="inline-flex items-center gap-1.5 text-[#6d28d9] cursor-pointer whitespace-nowrap"
                      data-cd-id="${safeId}"
                      role="button"
                      tabindex="0"
                    >
                      ${content}
                      <span
                        class="inline-flex items-center ml-[1px] align-middle transition-transform duration-200 ease"
                        data-chevron="${safeId}"
                      >
                        ${CHEVRON_ICON_SVG}
                      </span>
                    </span>
                    <span
                      class="block w-full"
                      data-cd-slot="${safeId}"
                    ></span>
                `;
            }
        );
    } catch (error) {
        console.error("Failed to inject reasoning buttons:", error);
        return html;
    }
}

export function findCdSlot(
    container: HTMLElement,
    cdId: string
): HTMLElement | null {
    try {
        if (!container || !cdId) {
            return null;
        }

        const slots = Array.from(
            container.querySelectorAll<HTMLElement>("[data-cd-slot]")
        );

        return (
            slots.find(
                (slot) => slot.getAttribute("data-cd-slot") === cdId
            ) ?? null
        );
    } catch (error) {
        console.error("Failed to find cognitive decision slot:", error);
        return null;
    }
}