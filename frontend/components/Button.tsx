"use client";

import clsx from "clsx";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

const variantStyles: Record<Variant, string> = {
  primary: "bg-accent text-white hover:bg-accent/90 disabled:bg-accent/40",
  secondary:
    "bg-surfaceRaised text-ink border border-borderLight hover:bg-surfaceRaised/70 disabled:opacity-40",
  ghost: "bg-transparent text-ink hover:bg-white/5 disabled:opacity-40",
  danger: "bg-danger/15 text-danger border border-danger/30 hover:bg-danger/25 disabled:opacity-40",
};

const sizeStyles: Record<Size, string> = {
  sm: "text-xs px-2.5 py-1.5 gap-1.5",
  md: "text-sm px-4 py-2 gap-2",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", loading, className, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          "focus-ring inline-flex items-center justify-center rounded-lg font-medium transition-colors duration-150",
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {loading && (
          <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
