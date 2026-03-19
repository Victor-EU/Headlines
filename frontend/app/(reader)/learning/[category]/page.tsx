import { redirect } from "next/navigation";

export default async function LegacyLearningCategoryRedirect({
  params,
}: {
  params: Promise<{ category: string }>;
}) {
  const { category } = await params;
  redirect(`/learning#${category}`);
}
